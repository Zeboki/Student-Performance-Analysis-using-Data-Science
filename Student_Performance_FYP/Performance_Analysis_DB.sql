-- Create the database
CREATE DATABASE IF NOT EXISTS Performance_Analysis_DB;
USE Performance_Analysis_DB;

-- ADMIN Table
CREATE TABLE Admin (
    Admin_ID INT AUTO_INCREMENT PRIMARY KEY,
    Admin_Name VARCHAR(50) UNIQUE NOT NULL,
    Admin_PW VARCHAR(255) NOT NULL
);

-- TEACHER Table (One Admin manages Many Teachers)
CREATE TABLE Teacher (
    Teacher_ID INT AUTO_INCREMENT PRIMARY KEY,
    Admin_ID INT,
    Teacher_Name VARCHAR(50) UNIQUE NOT NULL,
    Teacher_PW VARCHAR(255) NOT NULL,
    FOREIGN KEY (Admin_ID) REFERENCES Admin(admin_id) ON DELETE CASCADE
);

-- STUDENT Table (One Admin manages Many Students)
CREATE TABLE Student (
    Student_ID INT AUTO_INCREMENT PRIMARY KEY,
    Admin_ID INT,
    Student_Name VARCHAR(50),
    Student_PW VARCHAR(255) NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE CASCADE
);

-- ACADEMIC_RECORD Table (One Student has Many Academic Records)
CREATE TABLE Academic_Record (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    attendance_status FLOAT,
    assignment_scores FLOAT,
    previous_gpa FLOAT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE
);

-- PREDICTION Table (One Teacher generates Many Predictions; Links to Academic Record)
CREATE TABLE Prediction (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    record_id INT,
    predicted_score FLOAT,
    risk_level VARCHAR(50),
    FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (record_id) REFERENCES Academic_Record(record_id) ON DELETE CASCADE
);

-- Insert Default Admin, Teacher & Student for Demo
INSERT INTO Admin (Admin_Name, Admin_PW) 
VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'); -- Hash for 'admin123'

INSERT INTO Teacher (Admin_ID, Teacher_Name, Teacher_PW) 
VALUES (1, 'teacher', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'); -- Hash for 'admin123'

INSERT INTO Student (Admin_ID, Student_Name, Student_PW) 
VALUES (1, 'student', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'); -- Hash for 'admin123'