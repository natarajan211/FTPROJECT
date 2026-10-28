"""
leave_management.py - Leave Operations Module

Handles student leave applications and administrator review workflows
including approvals, rejections, comments, and leave history queries.
"""

from datetime import datetime
from database import fetch_all, fetch_one, execute_query


def validate_leave_dates(start_date_str, end_date_str):
    """
    Validate start and end dates.
    Ensures correct format (YYYY-MM-DD) and verifies end_date >= start_date.
    Returns (is_valid: bool, error_message: str, start_dt, end_dt)
    """
    try:
        start_dt = datetime.strptime(str(start_date_str).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False, "Invalid start date. Please use YYYY-MM-DD format (e.g. 2026-11-01).", None, None

    try:
        end_dt = datetime.strptime(str(end_date_str).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False, "Invalid end date. Please use YYYY-MM-DD format (e.g. 2026-11-03).", None, None

    if end_dt < start_dt:
        return False, "End date cannot be earlier than start date.", None, None

    return True, "", start_dt, end_dt


def submit_leave_request(student_id, start_date, end_date, reason):
    """
    Submit a new student leave request with status 'Pending'.
    """
    student_id = str(student_id).strip()
    if not student_id:
        return False, "Student ID is required."

    if not reason or not str(reason).strip():
        return False, "Please provide a reason for the leave application."

    is_valid, err_msg, start_dt, end_dt = validate_leave_dates(start_date, end_date)
    if not is_valid:
        return False, err_msg

    # Verify student exists
    if not fetch_one("SELECT student_id FROM students WHERE student_id = %s", (student_id,)):
        return False, f"Student ID '{student_id}' was not found in records."

    query = """
        INSERT INTO leave_requests (student_id, start_date, end_date, reason, status)
        VALUES (%s, %s, %s, %s, 'Pending')
    """
    res = execute_query(query, (student_id, str(start_dt), str(end_dt), str(reason).strip()))
    if res.get("success"):
        return True, "Leave application submitted successfully. Current status: Pending."
    return False, f"Failed to submit leave request: {res.get('error')}"


def get_student_leave_history(student_id):
    """
    Retrieve leave history for a specific authenticated student only.
    Enforces strict authorization by querying solely with the authenticated student's ID.
    """
    student_id = str(student_id).strip()
    query = """
        SELECT 
            leave_id, student_id, start_date, end_date, reason, 
            submitted_at, status, admin_comment, reviewed_at
        FROM leave_requests
        WHERE student_id = %s
        ORDER BY submitted_at DESC, leave_id DESC
    """
    return fetch_all(query, (student_id,))


def get_all_leave_requests(status_filter="All"):
    """
    Retrieve all leave requests with student names and departments for administrator review.
    Supports filtering by status ('All', 'Pending', 'Approved', 'Rejected').
    """
    base_query = """
        SELECT 
            lr.leave_id, lr.student_id, s.name AS student_name, s.department,
            lr.start_date, lr.end_date, lr.reason, lr.submitted_at,
            lr.status, lr.admin_comment, lr.reviewed_at, adm.username AS reviewer
        FROM leave_requests lr
        INNER JOIN students s ON lr.student_id = s.student_id
        LEFT JOIN admins adm ON lr.reviewed_by = adm.admin_id
    """
    if status_filter and status_filter != "All":
        query = base_query + " WHERE lr.status = %s ORDER BY lr.submitted_at DESC"
        return fetch_all(query, (status_filter,))
    else:
        query = base_query + " ORDER BY lr.submitted_at DESC"
        return fetch_all(query)


def search_leave_requests(keyword):
    """
    Search leave requests by student ID or student name.
    """
    pattern = f"%{str(keyword).strip()}%"
    query = """
        SELECT 
            lr.leave_id, lr.student_id, s.name AS student_name, s.department,
            lr.start_date, lr.end_date, lr.reason, lr.submitted_at,
            lr.status, lr.admin_comment, lr.reviewed_at, adm.username AS reviewer
        FROM leave_requests lr
        INNER JOIN students s ON lr.student_id = s.student_id
        LEFT JOIN admins adm ON lr.reviewed_by = adm.admin_id
        WHERE lr.student_id LIKE %s OR s.name LIKE %s
        ORDER BY lr.submitted_at DESC
    """
    return fetch_all(query, (pattern, pattern))


def review_leave_request(leave_id, status, admin_comment="", reviewed_by=None):
    """
    Update a leave request status to 'Approved' or 'Rejected' with an optional admin comment.
    """
    if status not in ["Approved", "Rejected"]:
        return False, "Invalid status. Must be 'Approved' or 'Rejected'."

    query = """
        UPDATE leave_requests
        SET status = %s, admin_comment = %s, reviewed_at = NOW(), reviewed_by = %s
        WHERE leave_id = %s
    """
    res = execute_query(query, (status, str(admin_comment).strip() if admin_comment else None, reviewed_by, leave_id))
    if res.get("success"):
        return True, f"Leave request #{leave_id} marked as '{status}'."
    return False, f"Failed to update leave request: {res.get('error')}"


def delete_leave_request(leave_id):
    """
    Delete a leave request (used by administrator for duplicates or inappropriate requests).
    """
    query = "DELETE FROM leave_requests WHERE leave_id = %s"
    res = execute_query(query, (leave_id,))
    if res.get("success") and res.get("rowcount", 0) > 0:
        return True, f"Leave request #{leave_id} deleted successfully."
    return False, f"Failed to delete leave request: {res.get('error')}"
