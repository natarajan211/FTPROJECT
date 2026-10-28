"""
auth.py - Authentication and Security Module

Handles secure password hashing using PBKDF2-HMAC-SHA256 with cryptographically
random salts, along with role-based authentication for Administrators and Students.
"""

import hashlib
import secrets
import hmac
from database import fetch_one, execute_query


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256 with a unique random salt.
    Format returned: pbkdf2_sha256$100000$<salt>$<hash>
    """
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    salt = secrets.token_hex(16)
    iterations = 100000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a plaintext password against the stored salted hash using constant-time comparison.
    """
    if not stored_hash or not plain_password:
        return False
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hash = parts[3]

        derived = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        )
        return hmac.compare_digest(derived.hex(), expected_hash)
    except Exception as e:
        print(f"Error during password verification: {e}")
        return False


def initialize_admin():
    """
    Ensures the default admin account (NATARAJAN / NATARAJAN) exists.
    Created ONLY if an admin with username 'NATARAJAN' does not already exist.
    Restarting the application will NEVER overwrite or reset an existing admin's password.
    """
    query = "SELECT admin_id FROM admins WHERE username = %s LIMIT 1"
    existing = fetch_one(query, ("NATARAJAN",))
    if not existing:
        hashed = hash_password("NATARAJAN")
        insert_query = "INSERT INTO admins (username, password_hash) VALUES (%s, %s)"
        res = execute_query(insert_query, ("NATARAJAN", hashed))
        if res.get("success"):
            print("Default admin account (NATARAJAN) initialized successfully.")
        else:
            print(f"Admin initialization notice: {res.get('error')}")


def authenticate_admin(username: str, plain_password: str):
    """
    Authenticate an administrator by username and password.
    Returns admin details dictionary on success, or None on failure.
    """
    if not username or not plain_password:
        return None
    query = "SELECT admin_id, username, password_hash, created_at FROM admins WHERE username = %s"
    admin = fetch_one(query, (username.strip(),))
    if admin and verify_password(plain_password, admin["password_hash"]):
        # Do not keep password hash in session dictionary
        return {
            "admin_id": admin["admin_id"],
            "username": admin["username"],
            "created_at": admin["created_at"],
            "role": "admin"
        }
    return None


def change_admin_password(admin_id: int, old_password: str, new_password: str):
    """
    Allow an admin to safely change their password after verifying the old password.
    Returns (success: bool, message: str)
    """
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    admin = fetch_one("SELECT password_hash FROM admins WHERE admin_id = %s", (admin_id,))
    if not admin:
        return False, "Admin account not found."

    if not verify_password(old_password, admin["password_hash"]):
        return False, "Current password is incorrect."

    new_hash = hash_password(new_password)
    res = execute_query("UPDATE admins SET password_hash = %s WHERE admin_id = %s", (new_hash, admin_id))
    if res.get("success"):
        return True, "Password changed successfully."
    return False, f"Failed to update password: {res.get('error')}"


def authenticate_student(username: str, plain_password: str):
    """
    Authenticate a student by their login username and password.
    Only allows active accounts.
    Returns combined student profile and account details dictionary on success, or None on failure.
    """
    if not username or not plain_password:
        return None
    query = """
        SELECT 
            sa.account_id, sa.student_id, sa.username, sa.password_hash, sa.is_active,
            s.name, s.age, s.gender, s.course, s.department, s.year_of_study,
            s.email, s.phone, s.address, s.created_at AS profile_created_at
        FROM student_accounts sa
        INNER JOIN students s ON sa.student_id = s.student_id
        WHERE sa.username = %s
    """
    account = fetch_one(query, (username.strip(),))
    if account:
        if not account["is_active"]:
            return {"error": "Account is inactive. Please contact the administrator."}
        if verify_password(plain_password, account["password_hash"]):
            account.pop("password_hash", None)
            account["role"] = "student"
            return account
    return None


def create_student_account(student_id: str, username: str, plain_password: str):
    """
    Create login credentials for an existing student.
    Ensures student_id exists and username is unique.
    """
    student_id = student_id.strip()
    username = username.strip()

    # 1. Check if student exists in profile table
    student = fetch_one("SELECT student_id, name FROM students WHERE student_id = %s", (student_id,))
    if not student:
        return False, f"Student ID '{student_id}' does not exist in student records."

    # 2. Check if student already has an account
    existing_acc = fetch_one("SELECT account_id FROM student_accounts WHERE student_id = %s", (student_id,))
    if existing_acc:
        return False, f"Student '{student_id}' already has a login account."

    # 3. Check if username is taken
    existing_user = fetch_one("SELECT account_id FROM student_accounts WHERE username = %s", (username,))
    if existing_user:
        return False, f"Username '{username}' is already in use. Please choose a different username."

    if len(plain_password) < 4:
        return False, "Password must be at least 4 characters long."

    hashed = hash_password(plain_password)
    res = execute_query(
        "INSERT INTO student_accounts (student_id, username, password_hash, is_active) VALUES (%s, %s, %s, TRUE)",
        (student_id, username, hashed)
    )
    if res.get("success"):
        return True, f"Login account created successfully for {student['name']} ({student_id})."
    return False, f"Failed to create account: {res.get('error')}"


def reset_student_password(student_id: str, new_password: str):
    """
    Reset a student's password by the admin.
    """
    if len(new_password) < 4:
        return False, "New password must be at least 4 characters long."

    acc = fetch_one("SELECT account_id FROM student_accounts WHERE student_id = %s", (student_id.strip(),))
    if not acc:
        return False, f"No login account found for Student ID '{student_id}'."

    new_hash = hash_password(new_password)
    res = execute_query(
        "UPDATE student_accounts SET password_hash = %s WHERE student_id = %s",
        (new_hash, student_id.strip())
    )
    if res.get("success"):
        return True, "Student password reset successfully."
    return False, f"Failed to reset password: {res.get('error')}"
