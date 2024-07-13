-- Create the database
CREATE DATABASE IF NOT EXISTS students1;

-- Switch to the newly created database
USE students1;

-- Create the students table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    Email VARCHAR(100),
    phone_no VARCHAR(20),
    remark LONGTEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create an index on the full_name column for faster searches
CREATE INDEX idx_full_name ON students(full_name);

-- Create an index on the Email column for faster searches
CREATE INDEX idx_email ON students(Email);

-- Grant privileges to the application user
-- Replace 'your_app_username' and 'your_app_password' with actual values
GRANT SELECT, INSERT, UPDATE, DELETE ON students1.* TO 'your_app_username'@'localhost' IDENTIFIED BY 'your_app_password';

-- Flush privileges to ensure the changes take effect
FLUSH PRIVILEGES;
