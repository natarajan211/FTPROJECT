"""
student_management.py - Student Operations Module

Handles adding, retrieving, searching, updating, and deleting student records.
Also provides data validation for all student profile fields.
"""

import re
from database import fetch_all, fetch_one, execute_query


def validate_student_data(student_id, name, age, gender, course, department, year_of_study, email, phone):
    """
    Validate student input fields.
    Returns (is_valid: bool, error_message: str)
    """
    if not student_id or not str(student_id).strip():
        return False, "Student ID cannot be empty."
    if not name or not str(name).strip():
        return False, "Student name cannot be empty."
    
    try:
        age_int = int(age)
        if age_int < 15 or age_int > 100:
            return False, "Age must be a valid number between 15 and 100."
    except (ValueError, TypeError):
        return False, "Age must be an integer."

    if not gender or gender not in ["Male", "Female", "Other"]:
        return False, "Please select a valid gender (Male, Female, or Other)."

    if not course or not str(course).strip():
        return False, "Course cannot be empty."
    if not department or not str(department).strip():
        return False, "Department cannot be empty."
    if not year_of_study or not str(year_of_study).strip():
        return False, "Year of study cannot be empty."

    # Email validation regex
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not email or not re.match(email_regex, str(email).strip()):
        return False, "Please enter a valid email address (e.g., student@college.edu)."

    # Phone validation (at least 7 to 15 digits)
    phone_clean = re.sub(r"[\s\-\+]", "", str(phone))
    if not phone_clean.isdigit() or len(phone_clean) < 7 or len(phone_clean) > 15:
        return False, "Phone number must contain between 7 and 15 digits."

    return True, ""


def add_student(student_id, name, age, gender, course, department, year_of_study, email, phone, address=""):
    """
    Add a new student record to the database after validating fields.
    """
    is_valid, msg = validate_student_data(student_id, name, age, gender, course, department, year_of_study, email, phone)
    if not is_valid:
        return False, msg

    student_id = str(student_id).strip().upper()
    name = str(name).strip()
    email = str(email).strip().lower()
    phone = str(phone).strip()
    address = str(address).strip() if address else ""

    # Check for existing student_id
    if fetch_one("SELECT student_id FROM students WHERE student_id = %s", (student_id,)):
        return False, f"A student with ID '{student_id}' already exists."

    # Check for existing email
    if fetch_one("SELECT student_id FROM students WHERE email = %s", (email,)):
        return False, f"Email '{email}' is already registered with another student."

    query = """
        INSERT INTO students (student_id, name, age, gender, course, department, year_of_study, email, phone, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    res = execute_query(query, (student_id, name, int(age), gender, course, department, year_of_study, email, phone, address))
    if res.get("success"):
        return True, f"Student '{name}' ({student_id}) added successfully."
    return False, f"Failed to add student: {res.get('error')}"


def get_all_students():
    """
    Retrieve all student records along with their login account username (if created).
    """
    query = """
        SELECT 
            s.student_id, s.name, s.age, s.gender, s.course, s.department, 
            s.year_of_study, s.email, s.phone, s.address, s.created_at,
            sa.username AS account_username, sa.is_active AS account_active
        FROM students s
        LEFT JOIN student_accounts sa ON s.student_id = sa.student_id
        ORDER BY s.student_id ASC
    """
    return fetch_all(query)


def get_student_by_id(student_id):
    """
    Retrieve full details of an individual student by Student ID.
    """
    query = """
        SELECT 
            s.student_id, s.name, s.age, s.gender, s.course, s.department, 
            s.year_of_study, s.email, s.phone, s.address, s.created_at,
            sa.username AS account_username, sa.is_active AS account_active
        FROM students s
        LEFT JOIN student_accounts sa ON s.student_id = sa.student_id
        WHERE s.student_id = %s
    """
    return fetch_one(query, (str(student_id).strip(),))


def search_students(keyword):
    """
    Search students by Student ID, Name, Department, or Course.
    """
    keyword = f"%{str(keyword).strip()}%"
    query = """
        SELECT 
            s.student_id, s.name, s.age, s.gender, s.course, s.department, 
            s.year_of_study, s.email, s.phone, s.address, s.created_at,
            sa.username AS account_username, sa.is_active AS account_active
        FROM students s
        LEFT JOIN student_accounts sa ON s.student_id = sa.student_id
        WHERE s.student_id LIKE %s OR s.name LIKE %s OR s.department LIKE %s OR s.course LIKE %s
        ORDER BY s.student_id ASC
    """
    return fetch_all(query, (keyword, keyword, keyword, keyword))


def update_student(student_id, name, age, gender, course, department, year_of_study, email, phone, address=""):
    """
    Update an existing student's profile details.
    """
    is_valid, msg = validate_student_data(student_id, name, age, gender, course, department, year_of_study, email, phone)
    if not is_valid:
        return False, msg

    student_id = str(student_id).strip()
    name = str(name).strip()
    email = str(email).strip().lower()
    phone = str(phone).strip()
    address = str(address).strip() if address else ""

    # Ensure student exists
    if not fetch_one("SELECT student_id FROM students WHERE student_id = %s", (student_id,)):
        return False, f"Student ID '{student_id}' does not exist."

    # Check email duplicate among other students
    existing_email = fetch_one("SELECT student_id FROM students WHERE email = %s AND student_id != %s", (email, student_id))
    if existing_email:
        return False, f"Email '{email}' is already registered to another student ({existing_email['student_id']})."

    query = """
        UPDATE students
        SET name = %s, age = %s, gender = %s, course = %s, department = %s,
            year_of_study = %s, email = %s, phone = %s, address = %s
        WHERE student_id = %s
    """
    res = execute_query(query, (name, int(age), gender, course, department, year_of_study, email, phone, address, student_id))
    if res.get("success"):
        return True, f"Student '{name}' ({student_id}) updated successfully."
    return False, f"Failed to update student: {res.get('error')}"


def delete_student(student_id):
    """
    Delete a student record. Cascades to student_accounts and leave_requests.
    """
    student_id = str(student_id).strip()
    student = fetch_one("SELECT name FROM students WHERE student_id = %s", (student_id,))
    if not student:
        return False, f"Student ID '{student_id}' not found."

    query = "DELETE FROM students WHERE student_id = %s"
    res = execute_query(query, (student_id,))
    if res.get("success") and res.get("rowcount", 0) > 0:
        return True, f"Student '{student['name']}' ({student_id}) and related records deleted successfully."
    return False, f"Failed to delete student: {res.get('error')}"
