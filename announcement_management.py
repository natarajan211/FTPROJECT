"""
announcement_management.py - Announcement Operations Module

Handles creation, retrieval, updating, and deletion of college announcements.
Includes functions for both admin management and student read-only view.
"""

from datetime import datetime, date
from database import fetch_all, fetch_one, execute_query


def validate_announcement(title, message, published_at):
    """
    Validate announcement input fields.
    """
    if not title or not str(title).strip():
        return False, "Announcement title cannot be empty."
    if not message or not str(message).strip():
        return False, "Announcement message cannot be empty."
    if not published_at:
        return False, "Announcement date is required."

    # Validate date format (YYYY-MM-DD or date object)
    if isinstance(published_at, (datetime, date)):
        return True, ""
    
    try:
        datetime.strptime(str(published_at).strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD (e.g. 2026-10-30)."


def create_announcement(title, message, published_at=None, created_by=None, is_published=True):
    """
    Publish or save a new announcement.
    """
    if published_at is None:
        published_at = date.today().strftime("%Y-%m-%d")

    is_valid, err = validate_announcement(title, message, published_at)
    if not is_valid:
        return False, err

    query = """
        INSERT INTO announcements (title, message, published_at, created_by, is_published)
        VALUES (%s, %s, %s, %s, %s)
    """
    res = execute_query(query, (str(title).strip(), str(message).strip(), published_at, created_by, bool(is_published)))
    if res.get("success"):
        return True, "Announcement published successfully."
    return False, f"Failed to save announcement: {res.get('error')}"


def get_all_announcements():
    """
    Retrieve all announcements (both published and drafts) for administrator view.
    """
    query = """
        SELECT 
            a.announcement_id, a.title, a.message, a.published_at, 
            a.is_published, adm.username AS author
        FROM announcements a
        LEFT JOIN admins adm ON a.created_by = adm.admin_id
        ORDER BY a.published_at DESC, a.announcement_id DESC
    """
    return fetch_all(query)


def get_published_announcements():
    """
    Retrieve only published announcements for the Student Dashboard.
    Sorted with latest announcements first.
    """
    query = """
        SELECT 
            announcement_id, title, message, published_at
        FROM announcements
        WHERE is_published = TRUE
        ORDER BY published_at DESC, announcement_id DESC
    """
    return fetch_all(query)


def update_announcement(announcement_id, title, message, published_at, is_published=True):
    """
    Update an existing announcement.
    """
    is_valid, err = validate_announcement(title, message, published_at)
    if not is_valid:
        return False, err

    query = """
        UPDATE announcements
        SET title = %s, message = %s, published_at = %s, is_published = %s
        WHERE announcement_id = %s
    """
    res = execute_query(query, (str(title).strip(), str(message).strip(), published_at, bool(is_published), announcement_id))
    if res.get("success"):
        return True, "Announcement updated successfully."
    return False, f"Failed to update announcement: {res.get('error')}"


def delete_announcement(announcement_id):
    """
    Delete an announcement by ID.
    """
    query = "DELETE FROM announcements WHERE announcement_id = %s"
    res = execute_query(query, (announcement_id,))
    if res.get("success") and res.get("rowcount", 0) > 0:
        return True, "Announcement deleted successfully."
    return False, f"Failed to delete announcement: {res.get('error')}"


def search_announcements(keyword):
    """
    Search announcements by title or message keyword.
    """
    pattern = f"%{str(keyword).strip()}%"
    query = """
        SELECT 
            a.announcement_id, a.title, a.message, a.published_at, 
            a.is_published, adm.username AS author
        FROM announcements a
        LEFT JOIN admins adm ON a.created_by = adm.admin_id
        WHERE a.title LIKE %s OR a.message LIKE %s
        ORDER BY a.published_at DESC, a.announcement_id DESC
    """
    return fetch_all(query, (pattern, pattern))
