-- ============================================================
-- Student Management System Database Schema
-- Database: student_management
-- Designed for MySQL Server 8.0+
-- ============================================================

-- 1. Create Database if not exists
CREATE DATABASE IF NOT EXISTS student_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_management;

-- 2. Drop existing tables if re-running (in reverse foreign-key order)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS leave_requests;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS student_accounts;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;
SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- Table 1: admins
-- Purpose: Stores administrative login credentials and audit info.
-- ------------------------------------------------------------
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table 2: students
-- Purpose: Stores student biographical and academic profile data.
-- ------------------------------------------------------------
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    course VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    year_of_study VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_name (name),
    INDEX idx_student_department (department)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table 3: student_accounts
-- Purpose: Stores student login credentials separated from profile data.
-- ------------------------------------------------------------
CREATE TABLE student_accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table 4: announcements
-- Purpose: Stores broadcast notices created by administrators.
-- ------------------------------------------------------------
CREATE TABLE announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    published_at DATE NOT NULL,
    created_by INT NULL,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_announcement_admin FOREIGN KEY (created_by)
        REFERENCES admins(admin_id)
        ON DELETE SET NULL,
    INDEX idx_announcement_date (published_at DESC)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table 5: leave_requests
-- Purpose: Stores student leave applications and admin approval decisions.
-- ------------------------------------------------------------
CREATE TABLE leave_requests (
    leave_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
    admin_comment TEXT NULL,
    reviewed_at DATETIME NULL,
    reviewed_by INT NULL,
    CONSTRAINT fk_leave_student FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_leave_admin FOREIGN KEY (reviewed_by)
        REFERENCES admins(admin_id)
        ON DELETE SET NULL,
    INDEX idx_leave_status (status),
    INDEX idx_leave_student (student_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Initial Sample Data for Demonstration
-- ------------------------------------------------------------

-- Note: The primary admin "NATARAJAN" is initialized automatically 
-- by auth.py using PBKDF2-HMAC-SHA256 salted hashing upon first run.

-- Insert Sample Students
INSERT INTO students (student_id, name, age, gender, course, department, year_of_study, email, phone, address)
VALUES
('STU101', 'Rahul Sharma', 20, 'Male', 'B.Tech', 'Computer Science & Engineering', '3rd Year', 'rahul.cs@college.edu', '9876543210', '12 Lake View Road, Chennai'),
('STU102', 'Priya Patel', 19, 'Female', 'B.Tech', 'Information Technology', '2nd Year', 'priya.it@college.edu', '9876543211', '45 Gandhi Street, Coimbatore'),
('STU103', 'Anand Kumar', 21, 'Male', 'B.E.', 'Mechanical Engineering', '4th Year', 'anand.mech@college.edu', '9876543212', '78 Nehru Nagar, Madurai');

-- Note: Student accounts will be created through the Admin Dashboard,
-- or automatically initialized if running sample tests.

-- Insert Sample Announcements
INSERT INTO announcements (title, message, published_at, is_published)
VALUES
('College Reopening Notice', 'Odd semester regular offline classes commence from next Monday at 8:30 AM.', CURDATE(), TRUE),
('Mid-Semester Examination Schedule', 'Mid-Term Examinations for all 2nd, 3rd, and 4th year students start from the 15th of next month.', CURDATE(), TRUE),
('Annual Technical Symposium', 'Registrations for the Inter-Collegiate Hackathon and Paper Presentation are now open on the department portal.', CURDATE(), TRUE);
