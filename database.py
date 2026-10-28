"""
database.py - Database Connection and Utility Operations

This module manages the connection to MySQL Server and provides helper functions
for executing queries safely using parameterized statements.
"""

import os
import json
import mysql.connector
from mysql.connector import Error

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "db_config.json")

# Default database connection settings
DEFAULT_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "student_management",
    "port": 3306
}


def load_db_config():
    """Load database settings from db_config.json or create with defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()
    else:
        # Create default config file for easy editing by beginners
        save_db_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_db_config(config_dict):
    """Save database settings to db_config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving database configuration: {e}")
        return False


def get_connection():
    """
    Establish and return a MySQL connection.
    Raises mysql.connector.Error if the connection fails.
    """
    config = load_db_config()
    return mysql.connector.connect(
        host=config.get("host", "localhost"),
        user=config.get("user", "root"),
        password=config.get("password", "root"),
        database=config.get("database", "student_management"),
        port=config.get("port", 3306),
        autocommit=False  # Explicit transaction control
    )


def test_connection():
    """
    Test connection to MySQL server.
    Returns (success: bool, message: str)
    """
    try:
        conn = get_connection()
        if conn.is_connected():
            conn.close()
            return True, "Successfully connected to MySQL database."
        return False, "Failed to connect to MySQL database."
    except Error as e:
        return False, f"MySQL Connection Error: {e.msg} (Code: {e.errno})"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def execute_query(query, params=None, commit=True):
    """
    Execute an INSERT, UPDATE, or DELETE query using parameterized inputs.
    Returns the number of affected rows or last insert ID.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
        last_id = cursor.lastrowid
        row_count = cursor.rowcount
        return {"success": True, "rowcount": row_count, "lastrowid": last_id, "error": None}
    except Error as err:
        if conn:
            conn.rollback()
        return {"success": False, "rowcount": 0, "lastrowid": None, "error": err.msg}
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def fetch_all(query, params=None):
    """
    Execute a SELECT query and return all matching rows as a list of dictionaries.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        records = cursor.fetchall()
        return records
    except Error as err:
        print(f"Database Fetch Error: {err.msg}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def fetch_one(query, params=None):
    """
    Execute a SELECT query and return a single row as a dictionary, or None.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        record = cursor.fetchone()
        return record
    except Error as err:
        print(f"Database Fetch One Error: {err.msg}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def initialize_database():
    """
    Create the database and tables if they do not exist.
    Reads database.sql located in the same directory.
    """
    config = load_db_config()
    db_name = config.get("database", "student_management")
    
    # 1. Connect without selecting database to ensure database exists
    try:
        root_conn = mysql.connector.connect(
            host=config.get("host", "localhost"),
            user=config.get("user", "root"),
            password=config.get("password", "root"),
            port=config.get("port", 3306)
        )
        root_cursor = root_conn.cursor()
        root_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        root_conn.commit()
        root_cursor.close()
        root_conn.close()
    except Error as e:
        print(f"Notice during database check: {e.msg}")

    # 2. Execute table creation script
    sql_path = os.path.join(os.path.dirname(__file__), "database.sql")
    if os.path.exists(sql_path):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            with open(sql_path, "r", encoding="utf-8") as f:
                content = f.read()

            for statement in content.split(";"):
                stmt = statement.strip()
                # Skip DROP and SET statements during auto-init so we don't wipe existing data
                if stmt and not stmt.upper().startswith("DROP") and not stmt.upper().startswith("SET"):
                    try:
                        cursor.execute(stmt)
                    except Error:
                        pass  # Table or record may already exist
            conn.commit()
            cursor.close()
            conn.close()
            print("Database tables initialized successfully.")
        except Exception as e:
            print(f"Database initialization info: {e}")
