# Faculty Management System (FMS)

A comprehensive, Flask-based web application for managing faculty workloads, academic schedules, analytics, and HR processes.

![Banner](https://via.placeholder.com/1200x300?text=Faculty+Management+System)

## 🚀 Key Features

### 🏢 Admin Dashboard
*   **Academics Center**: Manage Departments, Subjects, Classes, and Classrooms.
*   **Schedule Center**:
    *   **Timetable Editor**: Drag-and-drop style slot management.
    *   **Conflict Engine**: Automatic detection of faculty/room overlaps.
    *   **Smart Suggestions**: Recommends available slots for rescheduling.
*   **HR Center**:
    *   **Attendance Manager**: Track daily faculty attendance.
    *   **Leave Management**: Approve/Reject leave requests.
    *   **Academic Calendar**: Manage holidays and exam dates.
*   **Analytics**: Visual dashboards for workload distribution, faculty stats, and leave trends.
*   **Data Export**: PDF reports (Timetables, Profiles) and Excel exports.

### 👨‍🏫 Faculty Portal
*   **Personal Dashboard**: View upcoming classes and weekly schedule.
*   **Leave Application**: Apply for leave and track status.
*   **Profile Management**: Update personal details and password.

---

## 🛠️ Technology Stack
*   **Backend**: Python, Flask, SQLAlchemy (ORM)
*   **Frontend**: HTML5, Bootstrap 5, Jinja2, Chart.js, FontAwesome
*   **Database**: SQLite (default), extensible to PostgreSQL
*   **Tools**: Flask-Migrate, XHTML2PDF, Pandas

---

## 📦 Installation & Setup

### Option 1: Quick Setup (Windows)
Simply run the included batch script to automate everything:
1.  Double-click **`setup.bat`**
2.  Follow the on-screen prompts to:
    *   Create a virtual environment.
    *   Install dependencies.
    *   Initialize and seed the database.
    *   **Create an Admin User** interactively.

### Option 2: Manual Setup
If you prefer identifying the steps manually:

1.  **Create Virtual Environment**:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    # source .venv/bin/activate  # Mac/Linux
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Database**:
    ```bash
    flask init-db
    flask seed-db  # Optional: Adds dummy data
    ```

4.  **Create Admin User**:
    ```bash
    flask create-admin
    # Follow prompts for username and password
    ```

---

## 🚦 Usage

### Running the Application
```bash
python app.py
```
Or via Flask CLI:
```bash
flask run --debug
```
Access the app at: **http://127.0.0.1:5000**

### Default Login
If you seeded the database or created an admin:
*   **Admin Login**: Use the credentials you set up.
*   **Faculty Login**: Use the email of any seeded faculty member (password matches config default or set manually).

---

## 📂 Project Structure

```
faculty_management/
├── app.py                 # Application factory & entry point
├── commands.py            # CLI commands (init-db, create-admin)
├── config.py              # Configuration classes
├── models.py              # Database models
├── forms.py               # WTForms definitions
├── setup.bat              # Quick setup script
│
├── routes/                # Modular Route Blueprints
│   ├── admin/             # Admin modules (Faculty, Schedule, HR, Analytics)
│   ├── faculty_routes.py  # Faculty portal routes
│   └── auth_routes.py     # Authentication routes
│
├── templates/             # Jinja2 HTML Templates
│   ├── admin/             # Admin views
│   ├── faculty/           # Faculty views
│   └── reports/           # PDF export templates
│
└── static/                # CSS, JS, Images
    └── css/custom.css     # Global styling
```

## 🤝 Contributing
1.  Fork the repository.
2.  Create a feature branch.
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

## 📄 License
This project is licensed under the MIT License.
