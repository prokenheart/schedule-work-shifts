import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import re
from ortools.sat.python import cp_model
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from dotenv import load_dotenv

load_dotenv()




def run_scheduler():
    SHEET_ID = os.getenv("SHEET_ID")

    service_account_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT"]
    )

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)


    def get_list_from_cell(worksheet, cell):
        result = worksheet.get(cell)

        # Nếu ô trống hoặc không có dữ liệu → trả về list rỗng
        if not result or not result[0]:
            return []
        # Lấy chuỗi từ ô (ví dụ "Khang, Nuu" hoặc "Khang Nuu")
        raw_value = result[0][0]

        # Chuẩn hóa: chuyển về dạng chữ thường trước
        raw_value = raw_value.lower().strip()

        # Tách theo dấu phẩy hoặc khoảng trắng liên tiếp
        names = re.split(r'[,\s]+', raw_value)

        # Viết hoa chữ cái đầu, loại bỏ chuỗi rỗng nếu có
        clean_names = [name.capitalize() for name in names if name]

        return clean_names


    worksheet = client.open_by_key(SHEET_ID).sheet1

    # Lấy dữ liệu từ B4:I7
    raw_data = worksheet.get("B4:I7")
    df = pd.DataFrame(raw_data[1:], columns=["Ca"] + raw_data[0][1:])


    # Chuẩn hóa dữ liệu trong từng ô
    for column in df.columns[1:]:
        df[column] = df[column].fillna("")
        for idx in df.index:
            raw = df.at[idx, column]
            cleaned = re.sub(r"[.,]?\s+", ",", raw.strip())  # Phúc. Hân  -> Phúc,Hân; Phúc Hân -> Phúc,Hân
            emps = [e.strip().capitalize() for e in cleaned.split(",") if e.strip()]
            df.at[idx, column] = emps

    full_time_emps = get_list_from_cell(worksheet, "I9")
    # print(full_time_emps)               # có thể thêm nhiều tên
    for column in df.columns[1:]:       # duyệt các ngày (bỏ cột Ca)
        df[column] = df[column].apply(
            lambda lst: sorted(set(lst + full_time_emps))   # bảo đảm duy nhất + sắp xếp
        )

    # print("Dữ liệu đã chuẩn hóa:")
    # print(df)

    # Lấy danh sách tất cả nhân viên
    employees = sorted({emp for col in df.columns[1:] for row in df[col] for emp in row})
    # In danh sách nhân viên
    # print("\nDanh sách nhân viên:")
    # for emp in employees:
    #     print(emp)


    # Giờ mỗi ca (tính theo đơn vị 1/10 giờ để tránh số thực)
    hours_per_shift = {0: 35, 1: 50, 2: 50}  # ca 0, 1, 2 tương đương Ca 1, 2, 3

    # Tính giờ đăng ký của mỗi người
    registered_hours = {emp: 0 for emp in employees}
    for ca_idx, row in df.iterrows():
        for day in df.columns[1:]:
            for emp in row[day]:
                registered_hours[emp] += hours_per_shift[ca_idx]

    # print("\nGiờ đăng ký của mỗi nhân viên:")
    # for emp, hours in registered_hours.items():
    #     print(f"{emp}: {hours/10} giờ")

    # Khởi tạo mô hình
    model = cp_model.CpModel()
    n_days = len(df.columns) - 1
    n_shifts = 3
    x = {}

    # Biến quyết định
    for i in employees:
        for j in range(n_days):
            for k in range(n_shifts):
                x[i, j, k] = model.NewBoolVar(f'x[{i},{j},{k}]')



    # Ràng buộc: mỗi ca đúng 2 người
    for j in range(n_days):
        for k in range(n_shifts):
            model.Add(sum(x[i, j, k] for i in employees) == 2)


    # Ràng buộc: chỉ gán nếu đã đăng ký
    for ca_idx, row in df.iterrows():
        for day_idx, day in enumerate(df.columns[1:]):
            allowed = set(row[day])
            for i in employees:
                if i not in allowed:
                    model.Add(x[i, day_idx, ca_idx] == 0)



    # Tổng giờ làm và độ lệch
    total_hours_assigned = {}
    for i in employees:
        total_hours_assigned[i] = sum(
            x[i, j, k] * hours_per_shift[k] for j in range(n_days) for k in range(n_shifts)
        )

    SCALE = 100

    # 1) thêm biến biên
    r_min = model.NewIntVar(0, SCALE, "r_min")
    r_max = model.NewIntVar(0, SCALE, "r_max")

    # 2) ràng buộc tỉ lệ cho từng nhân viên
    for i in employees:
        registered = registered_hours[i]          # hằng số
        model.Add(total_hours_assigned[i] * SCALE >= r_min * registered)
        model.Add(total_hours_assigned[i] * SCALE <= r_max * registered)

    emp_sorted = sorted(employees, key=lambda e: registered_hours[e], reverse=True)        # sắp theo giờ đăng ký GIẢM dần

    gap = 1   # % chênh lệch tối thiểu giữa hai người liền kề
    pending_hi = []

    for idx in range(len(emp_sorted) - 1):
        hi = emp_sorted[idx]
        lo = emp_sorted[idx + 1]

        if registered_hours[hi] == registered_hours[lo]:
            model.AddAbsEquality(
                model.NewIntVar(0, 25, f'diff_{hi}_{lo}'),
                total_hours_assigned[hi] - total_hours_assigned[lo]
            )
            pending_hi.append(hi)
        elif registered_hours[hi] > registered_hours[lo]:
            # Áp dụng ràng buộc cho tất cả những người trước đó có giờ đăng ký bằng nhau
            for emp_hi in pending_hi + [hi]:
                model.Add(
                    total_hours_assigned[emp_hi] * registered_hours[lo] * SCALE
                    >= (total_hours_assigned[lo] * SCALE + gap * registered_hours[lo]) * registered_hours[emp_hi]
                )
            pending_hi = []  # reset danh sách


    # ===> BẮT ĐẦU RÀNG BUỘC MỀM Ở ĐÂY <===

    penalties = []


    for i in employees:
        ca3_count = sum(x[i, j, 2] for j in range(n_days))

        # Ràng buộc mềm 1: >3 lần → phạt nhẹ
        over_ca3_3 = model.NewBoolVar(f'over_ca3_gt3_{i}')
        model.Add(ca3_count > 3).OnlyEnforceIf(over_ca3_3)
        model.Add(ca3_count <= 3).OnlyEnforceIf(over_ca3_3.Not())
        penalties.append((over_ca3_3, 3))

        # Ràng buộc mềm 2: >4 lần → phạt nặng
        over_ca3_4 = model.NewBoolVar(f'over_ca3_gt4_{i}')
        model.Add(ca3_count > 4).OnlyEnforceIf(over_ca3_4)
        model.Add(ca3_count <= 4).OnlyEnforceIf(over_ca3_4.Not())
        penalties.append((over_ca3_4, 5))


    # 🟡 Ràng buộc mềm 3: hạn chế làm liền ca 2 và 3
    for i in employees:
        for j in range(n_days):
            double_late = model.NewBoolVar(f'double_late_{i}_{j}')
            model.AddBoolAnd([x[i, j, 1], x[i, j, 2]]).OnlyEnforceIf(double_late)
            model.AddBoolOr([x[i, j, 1].Not(), x[i, j, 2].Not()]).OnlyEnforceIf(double_late.Not())
            penalties.append((double_late, 4))

    for i in employees:
        for j in range(n_days):
            shifts_per_day = [x[i, j, k] for k in range(n_shifts)]
            total_shifts = model.NewIntVar(0, n_shifts, f'total_shifts_{i}_{j}')
            model.Add(total_shifts == sum(shifts_per_day))

            # Tạo biến vi phạm nếu > 2 ca
            over_2_shifts = model.NewBoolVar(f'over_2_shifts_{i}_{j}')
            model.Add(total_shifts > 2).OnlyEnforceIf(over_2_shifts)
            model.Add(total_shifts <= 2).OnlyEnforceIf(over_2_shifts.Not())

            # Thêm vào danh sách penalties, ví dụ phạt 2 điểm
            penalties.append((over_2_shifts, 10))

    # ===> HÀM MỤC TIÊU <===
    model.Minimize((r_max - r_min) + sum(w * v for v, w in penalties))

    def debug_feasibility(employees, df):
        errors = []

        # --- 1. Kiểm tra mỗi ca có đủ người đăng ký hay không ---
        for day_idx, day in enumerate(df.columns[1:]):  # SỬA: bỏ cột "Ca"
            for k in range(3):  # ca 0,1,2
                required = 2
                available = 0

                # Lấy danh sách người đăng ký cho ca k vào ngày này
                registered_list = df.at[k, day]  # là list các tên (do bạn đã chuẩn hóa)

                for emp in employees:
                    if emp in registered_list:
                        available += 1

                if available < required:
                    errors.append(f"Ngày {day}, ca {k+1}: chỉ có {available}/2 người đăng ký.")

        # --- 2. Kiểm tra nhân viên đăng ký 0 giờ ---
        zero_regs = [e for e in employees if registered_hours[e] == 0]
        if zero_regs:
            errors.append("Nhân viên đăng ký 0 giờ (sẽ không được phân ca): " + ", ".join(zero_regs))

        # --- 3. Kiểm tra tổng giờ ---
        n_days = len(df.columns) - 1
        total_required_hours = 135 * n_days  # 3.5 + 5 + 5 = 13.5 giờ/ngày → 135 đơn vị
        total_registered_hours = sum(registered_hours.values())

        if total_registered_hours < total_required_hours:
            errors.append(
                f"Tổng giờ đăng ký ({total_registered_hours/10}h) < tổng giờ cần ({total_required_hours/10}h) → "
                "chắc chắn không đủ người!"
            )

        return errors

    issues = debug_feasibility(employees, df)

    if issues:
        print("⚠️ Có vấn đề về ràng buộc khiến mô hình có thể vô nghiệm:")
        for e in issues:
            print(" -", e)
    else:
        print("Không phát hiện lỗi trước solve.")


    # Giải mô hình
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    status = solver.Solve(model)
    
    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return {
            "status": "error",
            "message": "Không tìm được lời giải hợp lệ"
        }

    schedule = {}
    for j in range(n_days):
        day_name = f"Day{j+1}"
        schedule[day_name] = {}
        for k in range(n_shifts):
            schedule[day_name][f"Ca{k+1}"] = [
                i for i in employees if solver.Value(x[i, j, k])
            ]

    summary = []
    for i in employees:
        assigned = solver.Value(total_hours_assigned[i]) / 10
        registered = registered_hours[i] / 10
        ratio = assigned / registered * 100 if registered else 0

        summary.append({
            "name": i,
            "assigned_hours": round(assigned, 1),
            "registered_hours": round(registered, 1),
            "ratio": round(ratio, 1)
        })

    return {
        "status": "ok",
        "schedule": schedule,
        "summary": summary
    }

if __name__ == "__main__":
    result = run_scheduler()
    print(json.dumps(result, ensure_ascii=False))