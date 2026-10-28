# Student Management System

A desktop application built using **Python 3**, **Tkinter / ttk**, and **MySQL** (`mysql-connector-python`).

This system implements **Role-Based Access Control (RBAC)** featuring dedicated interfaces for **Administrators** and **Students**, salted password hashing with PBKDF2-HMAC-SHA256, parameterized SQL queries, and complete student lifecycle management.

---

## 📌 Project Overview

- **Project Name:** Student Management System
- **Language:** Python 3.8+
- **GUI Framework:** Tkinter & ttk (Native Python Standard Library)
- **Database:** MySQL Server 8.0+
- **Database Connector:** `mysql-connector-python`
- **Application Type:** Desktop Application
- **Security:** PBKDF2-HMAC-SHA256 salted password hashing, parameterized SQL queries, role-isolated sessions

---

## 📂 Project Structure

```
student_management_system/
│
├── database.sql               # MySQL database and table definition script
├── database.py                # Database connection pooling and helper operations
├── auth.py                    # PBKDF2 hashing, admin/student authentication & account management
├── student_management.py      # Student CRUD operations, search, and field validation
├── announcement_management.py # Announcement creation, publishing, editing, and retrieval
├── leave_management.py        # Leave application submission, approval/rejection workflows
├── admin_dashboard.py         # Tkinter GUI for the Administrator Portal
├── student_dashboard.py       # Tkinter GUI for the Student Portal (restricted read-only profile)
├── main.py                    # Application entry point, Welcome portal, and Login screens
├── requirements.txt           # Python dependencies
└── README.md                  # Complete documentation and setup guide
```

---

## 🚀 Quick Start Guide

### Step 1: Install Prerequisites

1. **Python 3.8+**: Ensure Python is installed and added to your system PATH.
2. **MySQL Server 8.0+**: Ensure MySQL Server is running on your machine (e.g., via MySQL Workbench, XAMPP, or Windows Service).

### Step 2: Install Python Package

In your terminal or command prompt:

```bash
pip install -r requirements.txt
```

*(Or `py -m pip install -r requirements.txt`)*

### Step 3: Set Up MySQL Database

Open **MySQL Workbench** or MySQL Command Line Client, and run the contents of [database.sql](file:///d:/pythonproject/student_management_system/database.sql):

```sql
SOURCE d:/pythonproject/student_management_system/database.sql;
```

*Alternatively, the application will automatically create the database and required tables upon first launch!*

### Step 4: Configure Database Connection (If Needed)

The application automatically connects with default credentials (`localhost`, user `root`, password `root`, port `3306`).
If your MySQL password is different, you can either:
1. Click **"⚙️ Database Connection Settings"** on the Welcome screen to test and save your credentials directly from the GUI, or
2. Edit [db_config.json](file:///d:/pythonproject/student_management_system/db_config.json):

```json
{
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "student_management",
    "port": 3306
}
```

### Step 5: Launch the Application

Run the entry point:

```bash
python main.py
```
*(Or `py main.py`)*

---

## 🔑 Default Credentials

### Administrator Portal
- **Username / Admin ID:** `NATARAJAN`
- **Password:** `NATARAJAN`

> [!NOTE]
> The admin password is automatically salted and hashed using PBKDF2-HMAC-SHA256 upon first launch. Restarting the application will **never** overwrite or reset your password if you modify it.

### Sample Student Credentials
Admin can create student credentials from the Admin Dashboard. A sample student account is provided:
- **Username:** `rahul101`
- **Password:** `rahul@123`
- **Student ID:** `STU101` (Rahul Sharma)

---

## 💻 Feature Guide

### 1. Administrator Dashboard
- **Student Management:**
  - Add new students with field validations (ID, Name, Age, Gender, Course, Department, Year, Email, Phone, Address).
  - Search students by Student ID, Name, or Department.
  - Edit and update existing student records.
  - Delete student records with safety confirmation dialogs (cascades cleanly).
  - Create student portal login accounts and reset student passwords.
  - Interactive Tkinter Treeview table with dual scrollbars.
- **Announcement Management:**
  - Create and publish college notices, exam alerts, and holiday circulars.
  - Edit or delete announcements.
  - Search announcements by title or content.
- **Leave Request Management:**
  - View all student leave requests with student details and date ranges.
  - Filter by status: All, Pending, Approved, Rejected.
  - Approve or Reject applications with custom admin remarks/comments.
  - Delete duplicate or inappropriate requests.
- **Admin Settings:**
  - Safely change the administrator password with old password verification.

### 2. Student Dashboard
- **My Profile:**
  - Strictly read-only view of academic, contact, and biographical records.
  - Students are restricted from editing or deleting official college records.
- **College Announcements:**
  - Live broadcast feed of notices published by administrators (ordered latest first).
  - Full notice text reader pane.
- **Apply for Leave:**
  - Date validation prevents end dates that precede start dates.
  - Mandatory reason field.
  - Submit request with instant status set to "Pending".
- **My Leave History:**
  - Displays **only** the authenticated student's leave applications.
  - Real-time status update: `Pending`, `Approved`, or `Rejected` along with administrator remarks.
