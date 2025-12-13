document.getElementById("btnSchedule").onclick = async () => {
    const res = await fetch("/api/schedule", { method: "POST" });
    const data = await res.json();

    if (data.status !== "ok") {
    alert("Sắp ca thất bại");
    return;
    }

    renderSchedule(data.schedule);
    renderSummary(data.summary);
};
  
function renderSchedule(schedule) {
    const table = document.getElementById("schedule-table");
    table.innerHTML = "";

    const days = Object.keys(schedule);
    const shifts = Object.keys(schedule[days[0]]);

    // Header: Ngày
    let header = "<tr><th>Ca / Ngày</th>";
    days.forEach(day => {
        header += `<th>${day}</th>`;
    });
    header += "</tr>";
    table.innerHTML += header;

    // Rows: Ca
    shifts.forEach(ca => {
        let row = `<tr><th>${ca}</th>`;
        days.forEach(day => {
        row += `<td>${schedule[day][ca].join(", ")}</td>`;
        });
        row += "</tr>";
        table.innerHTML += row;
    });
}
  
  
function renderSummary(summary) {
    const table = document.getElementById("summary-table");
    table.innerHTML = "";

    table.innerHTML += `
        <tr>
        <th>Nhân viên</th>
        <th>Giờ được xếp</th>
        <th>Tỉ lệ (%)</th>
        </tr>
    `;

    summary.forEach(e => {
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

    html2canvas(scheduleContainer, { scale: 2 }).then(canvas => {
        const link = document.createElement("a");
        link.download = "lich_lam_viec.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
    }).catch(err => {
        console.error("Xuất PNG thất bại:", err);
    });
};
