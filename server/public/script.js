var register;
var summary;

document.getElementById("btnSchedule").onclick = async () => {
    try {
        const res = await fetch("https://prokenheart.pythonanywhere.com/api/schedule");
        const data = await res.json();
        if (data.status !== "ok") {
            alert("Sắp ca thất bại: " + (data.message || ""));
            return;
        }
        renderSchedule(data.schedule);
        summary = data.summary;
        renderSummary(summary);
        renderEmployeePool(summary);
        register = data.register;
    } catch (err) {
        alert("Lỗi kết nối server");
    }
};
  
function renderSchedule(schedule) {
    const table = document.getElementById("schedule-table");
    table.innerHTML = "";

    const days = Object.keys(schedule);
    const shifts = Object.keys(schedule[days[0]]);

    // Header: Ngày
    let header = "<tr><th>Ca / Ngày</th>";
    const dayMap = {
        Day1: "Thứ 2",
        Day2: "Thứ 3",
        Day3: "Thứ 4",
        Day4: "Thứ 5",
        Day5: "Thứ 6",
        Day6: "Thứ 7",
        Day7: "Chủ nhật"
      };
    days.forEach(day => {
        header += `<th>${dayMap[day]}</th>`;
    });
    header += "</tr>";
    table.innerHTML += header;

    // Rows: Ca
    shifts.forEach(ca => {
        let row = `<tr><th>${ca}</th>`;
        days.forEach(day => {
            row += `
                <td class="shift-cell" data-day="${day}" data-shift="${ca}">
                    <div class="chip-container">
                        ${schedule[day][ca].map(name => renderEmpChip(name)).join("")}
                    </div>
                </td>
            `;

        });
        row += "</tr>";
        table.innerHTML += row;
    });
}

function renderEmpChip(name) {
    return `
        <div class="emp-chip">
            <span class="emp-name">${name}</span>
            <span class="emp-remove">✕</span>
        </div>
    `;
}
  
document.addEventListener("click", e => {
    if (e.target.classList.contains("emp-remove")) {
        const empName = e.target.closest(".emp-chip").querySelector(".emp-name").textContent;
        summary.forEach(emp => {
            if (emp.name === empName) {
                emp.assigned_hours -= getHoursForShift(
                    e.target.closest(".shift-cell").dataset.shift
                );
                emp.ratio = ((emp.assigned_hours / emp.registered_hours) * 100).toFixed(1);
            }
        });
        renderSummary(summary);
        e.target.closest(".emp-chip").remove();
    }
});
  
  
function renderSummary(summary) {
    const table = document.getElementById("summary-table");
    table.innerHTML = "";

    // Tạo header
    table.innerHTML += `
        <tr>
            <th>Nhân viên</th>
            <th>Giờ được xếp</th>
            <th>Tỉ lệ (%)</th>
        </tr>
    `;

    // Sắp xếp mảng summary giảm dần theo assigned_hours
    // Nếu giờ bằng nhau, sắp thêm theo tên tăng dần (tùy chọn, giúp ổn định thứ tự)
    const sortedSummary = [...summary].sort((a, b) => {
        if (b.assigned_hours !== a.assigned_hours) {
            return b.assigned_hours - a.assigned_hours; // Giảm dần giờ
        }
        return a.name.localeCompare(b.name); // Nếu giờ bằng, sắp tên A → Z
    });

    // Render các dòng dữ liệu theo thứ tự đã sắp xếp
    sortedSummary.forEach(e => {
        table.innerHTML += `
            <tr>
                <td>${e.name}</td>
                <td>${e.assigned_hours}</td>
                <td>${e.ratio}</td>
            </tr>
        `;
    });
}
  
document.getElementById("btnExport").onclick = () => {
    const scheduleContainer = document.getElementById("schedule-container");

    document.querySelectorAll(".emp-remove").forEach(el => el.style.display = "none");
    document.querySelectorAll(".emp-chip").forEach(el => el.style.border = "none");

    html2canvas(scheduleContainer, { scale: 2 }).then(canvas => {
        const link = document.createElement("a");
        link.download = "lich_lam_viec.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    }).catch(err => {
        console.error("Xuất PNG thất bại:", err);
    });

    document.querySelectorAll(".emp-remove").forEach(el => el.style.display = "inline");
    document.querySelectorAll(".emp-chip").forEach(el => el.style.border = "#3498db 1px solid");
};

function renderEmployeePool(summary) {
    const pool = document.getElementById("employee-pool");
    pool.innerHTML = "";
  
    summary.forEach(e => {
        pool.innerHTML += `
            <div class="emp-chip" draggable="true" data-name="${e.name}">
            ${e.name}
            </div>
        `;
    });
}

let draggedName = null;

document.addEventListener("dragstart", e => {
    const chip = e.target.closest(".emp-chip");
    if (!chip) return;

    draggedName = chip.dataset.name;
    updateDropAvailability(draggedName);
});


function updateDropAvailability(name) {
    document.querySelectorAll(".shift-cell").forEach(cell => {
        const day = cell.dataset.day;
        const shift = cell.dataset.shift;

        const allowed =
            register?.[day]?.[shift]?.includes(name);

        cell.classList.toggle("allowed", allowed);
        cell.classList.toggle("blocked", !allowed);
    });
}


document.addEventListener("dragover", e => {
    const cell = e.target.closest(".shift-cell");
    if (!cell) return;

    if (cell.classList.contains("allowed")) {
        e.preventDefault(); // cho phép drop
    }
});


  
document.addEventListener("drop", e => {
    const cell = e.target.closest(".shift-cell");
    const chipContainer = cell.querySelector(".chip-container");
    if (!cell || !draggedName) return;

    e.preventDefault();

    if (!cell.classList.contains("allowed")) return;

    if (cell.querySelectorAll(".emp-chip").length >= 2) {
        alert("Ca này đã đủ 2 người");
        return;
    }

    chipContainer.insertAdjacentHTML("beforeend", renderEmpChip(draggedName));
    summary.forEach(e => {
        if (e.name === draggedName) {
            e.assigned_hours += getHoursForShift(cell.dataset.shift);
            e.ratio = ((e.assigned_hours / e.registered_hours) * 100).toFixed(1);
        }
    });
    renderSummary(summary);
});

function getHoursForShift(shift) {
    switch (shift) {
        case "Ca1":
            return 3.5;
        case "Ca2":
            return 5;
        case "Ca3":
            return 5;
        default:
            return 0;
    }
}

document.addEventListener("dragend", () => {
    draggedName = null;
    document.querySelectorAll(".shift-cell")
        .forEach(c => c.classList.remove("allowed", "blocked"));
});

  