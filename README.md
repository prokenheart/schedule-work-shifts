# Schedule Work Shifts

An automatic work shift scheduling system for employees at **Bùi Lê**.\
This project helps generate weekly work schedules fairly and efficiently
based on employee registrations and predefined constraints.

🔗 **Live Demo:**\
https://schedule-buile.netlify.app/
Note: For some reasons, this link is not available any more

------------------------------------------------------------------------

## 📌 Features

-   Automatically assign work shifts for employees
-   Ensure fair distribution of working hours
-   Visualize scheduled shifts in a clear weekly table
-   Display total working hours for each employee
-   Export the schedule as an image (PNG)
-   Simple and user-friendly interface

------------------------------------------------------------------------

## 🧠 Scheduling Logic (Overview)

-   The week runs from **Monday to Sunday**
-   Each day has **3 shifts**
    -   Shift 1: 3.5 hours\
    -   Shift 2: 5 hours\
    -   Shift 3: 5 hours
-   Each shift requires **2 employees**
-   Employees can register their available shifts
-   The algorithm aims to:
    -   Balance assigned hours among employees
    -   Slightly prioritize employees who register for more hours

------------------------------------------------------------------------

## 🛠️ Technologies Used

### Frontend

-   HTML
-   CSS
-   Vanilla JavaScript

### Backend

-   Python

### Deployment Tools

-   **Netlify** -- Frontend deployment
-   **PythonAnywhere** -- Backend deployment

------------------------------------------------------------------------

## 📂 Project Structure

    schedule-work-shifts/
    │
    ├── frontend/
    │   ├── index.html
    │   ├── style.css
    │   └── script.js
    │
    ├── backend/
    │   └── scheduler.py
    │
    └── README.md

------------------------------------------------------------------------

## 🚀 Getting Started (Local Development)

### 1. Clone the repository

``` bash
git clone https://github.com/prokenheart/schedule-work-shifts.git
cd schedule-work-shifts
```

### 2. Run Backend (Python)

``` bash
python scheduler.py
```

### 3. Open Frontend

Simply open `index.html` in your browser or serve it using a local
server.

------------------------------------------------------------------------

## 🌐 Deployment

-   Frontend is deployed on **Netlify**
-   Backend API is deployed on **PythonAnywhere**
-   The frontend communicates with the backend via HTTP requests

------------------------------------------------------------------------

## 🎯 Use Case

This project was built specifically for managing employee shifts at
**Bùi Lê**, but it can be easily adapted for: - Coffee shops - Small
restaurants - Retail stores - Any business with shift-based work
schedules

------------------------------------------------------------------------

## 📈 Future Improvements

-   Employee login & authentication
-   Admin dashboard
-   Editable constraints (number of shifts, employees per shift)
-   Save schedules to database
-   Export to PDF / Excel

------------------------------------------------------------------------

## 👤 Author

**Nguyễn Hoàng Phúc (Proken Heart)**\
GitHub: https://github.com/prokenheart
