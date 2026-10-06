CREATE DATABASE campussphere;

USE campussphere;

CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    hod_name VARCHAR(100)
);

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    register_number VARCHAR(20) NOT NULL UNIQUE,
    student_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    date_of_birth DATE,
    gender VARCHAR(10),
    year_of_study INT,
    section VARCHAR(10),
    department_id INT,
    
    FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);

INSERT INTO departments (department_name, hod_name)
VALUES
('Artificial Intelligence and Data Science', 'Dr. Kumar'),
('Computer Science and Engineering', 'Dr. Ravi'),
('Information Technology', 'Dr. Priya'),
('Electronics and Communication Engineering', 'Dr. Arun'),
('Mechanical Engineering', 'Dr. Suresh');

SELECT * FROM departments;

INSERT INTO students
(register_number, student_name, email, phone, date_of_birth, gender, year_of_study, section, department_id)
VALUES
('24AD001', 'Ananya', 'ananya@gmail.com', '9876543210', '2006-05-12', 'Female', 2, 'A', 1),
('24AD002', 'Rahul', 'rahul@gmail.com', '9876543211', '2006-07-20', 'Male', 2, 'A', 1),
('24CS001', 'Kavin', 'kavin@gmail.com', '9876543212', '2006-03-15', 'Male', 2, 'B', 2),
('24IT001', 'Priya', 'priya@gmail.com', '9876543213', '2006-09-10', 'Female', 2, 'A', 3);

SELECT * FROM students;

CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    designation VARCHAR(50),
    department_id INT,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);

INSERT INTO faculty
(faculty_name, email, phone, designation, department_id)
VALUES
('Dr. Meena Kumar', 'meena@college.edu', '9876500011', 'Professor', 1),
('Dr. Arun Kumar', 'arun@college.edu', '9876500012', 'Associate Professor', 1),
('Dr. Priya Sharma', 'priya@college.edu', '9876500013', 'Assistant Professor', 2),
('Dr. Karthik Raj', 'karthik@college.edu', '9876500014', 'Professor', 3),
('Dr. Divya S', 'divya@college.edu', '9876500015', 'Assistant Professor', 4);

SELECT * FROM faculty;

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    semester INT,
    department_id INT,
    faculty_id INT,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
);

INSERT INTO courses
(course_code, course_name, credits, semester, department_id, faculty_id)
VALUES
('AD201', 'Database Management Systems', 4, 3, 1, 1),
('AD202', 'Artificial Intelligence', 4, 3, 1, 2),
('AD203', 'Data Structures', 4, 3, 1, 1),
('CS201', 'Database Management Systems', 4, 3, 2, 3),
('IT201', 'Web Technology', 4, 3, 3, 4),
('EC201', 'Digital Electronics', 3, 3, 4, 5);

SELECT * FROM courses;

CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE,
    academic_year VARCHAR(20),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id),

    UNIQUE(student_id, course_id)
);

INSERT INTO enrollments
(student_id, course_id, enrollment_date, academic_year)
VALUES
(1, 1, '2026-06-10', '2026-2027'),
(1, 2, '2026-06-10', '2026-2027'),
(1, 3, '2026-06-10', '2026-2027'),
(2, 1, '2026-06-10', '2026-2027'),
(2, 2, '2026-06-10', '2026-2027'),
(2, 3, '2026-06-10', '2026-2027'),
(3, 4, '2026-06-10', '2026-2027'),
(4, 5, '2026-06-10', '2026-2027');

SELECT
    s.student_name,
    c.course_code,
    c.course_name,
    e.academic_year
FROM enrollments e
JOIN students s
    ON e.student_id = s.student_id
JOIN courses c
    ON e.course_id = c.course_id;

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    total_classes INT NOT NULL,
    classes_attended INT NOT NULL,
    attendance_percentage DECIMAL(5,2),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
);


INSERT INTO attendance
(student_id, course_id, total_classes, classes_attended, attendance_percentage)
VALUES
(1, 1, 40, 36, 90.00),
(1, 2, 42, 38, 90.48),
(1, 3, 40, 34, 85.00),
(2, 1, 40, 28, 70.00),
(2, 2, 42, 35, 83.33),
(2, 3, 40, 30, 75.00),
(3, 4, 38, 32, 84.21),
(4, 5, 40, 37, 92.50);

SELECT * FROM attendance;

CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    exam_name VARCHAR(100) NOT NULL,
    exam_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    room_number VARCHAR(20),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
);

INSERT INTO exams
(course_id, exam_name, exam_date, start_time, end_time, room_number)
VALUES
(1, 'Internal Assessment 1', '2026-07-15', '09:30:00', '11:00:00', 'B201'),
(2, 'Internal Assessment 1', '2026-07-17', '09:30:00', '11:00:00', 'B202'),
(3, 'Internal Assessment 1', '2026-07-20', '09:30:00', '11:00:00', 'B203'),
(1, 'Internal Assessment 2', '2026-09-10', '09:30:00', '11:00:00', 'B201'),
(2, 'Internal Assessment 2', '2026-09-12', '09:30:00', '11:00:00', 'B202');

SELECT * FROM exams;

CREATE TABLE exam_registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    exam_id INT NOT NULL,
    registration_date DATE,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (exam_id)
        REFERENCES exams(exam_id),

    UNIQUE(student_id, exam_id)
);

INSERT INTO exam_registrations
(student_id, exam_id, registration_date)
VALUES
(1, 1, '2026-07-01'),
(1, 2, '2026-07-01'),
(1, 3, '2026-07-01'),
(2, 1, '2026-07-01'),
(2, 2, '2026-07-01'),
(2, 3, '2026-07-01'),
(3, 1, '2026-07-01'),
(4, 2, '2026-07-01');

CREATE TABLE results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    exam_id INT NOT NULL,
    marks DECIMAL(5,2) NOT NULL,
    grade VARCHAR(5),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (course_id)
        REFERENCES courses(course_id),

    FOREIGN KEY (exam_id)
        REFERENCES exams(exam_id)
);

INSERT INTO results
(student_id, course_id, exam_id, marks, grade)
VALUES
(1, 1, 1, 88, 'A+'),
(1, 2, 2, 91, 'O'),
(1, 3, 3, 82, 'A+'),
(2, 1, 1, 62, 'B+'),
(2, 2, 2, 78, 'A'),
(2, 3, 3, 69, 'B+'),
(3, 4, 1, 85, 'A+'),
(4, 5, 2, 93, 'O');

SELECT
    s.student_name,
    c.course_name,
    e.exam_name,
    r.marks,
    r.grade
FROM results r
JOIN students s
    ON r.student_id = s.student_id
JOIN courses c
    ON r.course_id = c.course_id
JOIN exams e
    ON r.exam_id = e.exam_id;


CREATE TABLE classrooms (
    classroom_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    building VARCHAR(100),
    capacity INT NOT NULL,
    room_type VARCHAR(50),
    availability_status VARCHAR(20) DEFAULT 'Available'
);

INSERT INTO classrooms
(room_number, building, capacity, room_type, availability_status)
VALUES
('B201', 'Block B', 60, 'Classroom', 'Available'),
('B202', 'Block B', 60, 'Classroom', 'Available'),
('B203', 'Block B', 50, 'Classroom', 'Available'),
('C101', 'Block C', 40, 'Laboratory', 'Available'),
('C102', 'Block C', 40, 'Laboratory', 'Available'),
('D201', 'Block D', 100, 'Seminar Hall', 'Available');

SELECT * FROM classrooms;

CREATE TABLE equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50),
    classroom_id INT,
    quantity INT DEFAULT 1,
    status VARCHAR(30) DEFAULT 'Working',
    purchase_date DATE,

    FOREIGN KEY (classroom_id)
        REFERENCES classrooms(classroom_id)
);

INSERT INTO equipment
(equipment_name, equipment_type, classroom_id, quantity, status, purchase_date)
VALUES
('Desktop Computer', 'Computer', 4, 30, 'Working', '2025-06-15'),
('Projector', 'Display', 1, 1, 'Working', '2025-07-10'),
('Projector', 'Display', 2, 1, 'Working', '2025-07-10'),
('Air Conditioner', 'Cooling', 1, 2, 'Working', '2024-05-20'),
('Printer', 'Printer', 4, 2, 'Working', '2025-01-15'),
('Desktop Computer', 'Computer', 5, 35, 'Working', '2025-06-20'),
('Projector', 'Display', 6, 1, 'Under Maintenance', '2024-08-12');

SELECT * FROM equipment;

CREATE TABLE room_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT NOT NULL,
    faculty_id INT,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    purpose VARCHAR(200),
    booking_status VARCHAR(30) DEFAULT 'Confirmed',

    FOREIGN KEY (classroom_id)
        REFERENCES classrooms(classroom_id),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
);

INSERT INTO room_bookings
(classroom_id, faculty_id, booking_date, start_time, end_time, purpose, booking_status)
VALUES
(1, 1, '2026-10-05', '09:00:00', '11:00:00', 'DBMS Class', 'Confirmed'),
(2, 2, '2026-10-05', '10:00:00', '12:00:00', 'AI Class', 'Confirmed'),
(4, 1, '2026-10-06', '09:00:00', '12:00:00', 'DBMS Laboratory', 'Confirmed'),
(6, 3, '2026-10-07', '14:00:00', '16:00:00', 'Department Seminar', 'Confirmed');

SELECT * FROM room_bookings;

CREATE TABLE maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    reported_date DATE NOT NULL,
    problem_description VARCHAR(255),
    assigned_to VARCHAR(100),
    maintenance_status VARCHAR(30) DEFAULT 'Pending',
    completion_date DATE,

    FOREIGN KEY (equipment_id)
        REFERENCES equipment(equipment_id)
);

INSERT INTO maintenance
(equipment_id, reported_date, problem_description, assigned_to, maintenance_status, completion_date)
VALUES
(7, '2026-09-20', 'Projector display not working', 'Technical Team', 'In Progress', NULL),
(1, '2026-09-22', 'Two computers not powering on', 'IT Support', 'Completed', '2026-09-24');

SELECT * FROM maintenance;

SELECT
    rb.booking_id,
    c.room_number,
    c.room_type,
    f.faculty_name,
    rb.booking_date,
    rb.start_time,
    rb.end_time,
    rb.purpose,
    rb.booking_status
FROM room_bookings rb
JOIN classrooms c
    ON rb.classroom_id = c.classroom_id
JOIN faculty f
    ON rb.faculty_id = f.faculty_id;

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL UNIQUE,
    industry VARCHAR(100),
    location VARCHAR(100),
    website VARCHAR(150)
);

INSERT INTO companies
(company_name, industry, location, website)
VALUES
('TCS', 'Information Technology', 'Chennai', 'https://www.tcs.com'),
('Infosys', 'Information Technology', 'Bangalore', 'https://www.infosys.com'),
('Accenture', 'Information Technology', 'Bangalore', 'https://www.accenture.com'),
('Wipro', 'Information Technology', 'Chennai', 'https://www.wipro.com'),
('Zoho', 'Software', 'Chennai', 'https://www.zoho.com'),
('Amazon', 'E-Commerce and Cloud', 'Bangalore', 'https://www.amazon.com'),
('Microsoft', 'Software', 'Hyderabad', 'https://www.microsoft.com');

SELECT * FROM companies;

CREATE TABLE placement_drives (
    drive_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    package_lpa DECIMAL(5,2),
    minimum_cgpa DECIMAL(4,2),
    minimum_attendance DECIMAL(5,2),
    drive_date DATE,
    application_deadline DATE,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
);

INSERT INTO placement_drives
(company_id, job_role, package_lpa, minimum_cgpa, minimum_attendance, drive_date, application_deadline)
VALUES
(1, 'Software Developer', 7.50, 7.00, 75.00, '2026-10-15', '2026-10-10'),
(2, 'Systems Engineer', 6.50, 6.50, 75.00, '2026-10-18', '2026-10-12'),
(3, 'Application Developer', 8.00, 7.50, 80.00, '2026-10-20', '2026-10-14'),
(4, 'Project Engineer', 6.00, 6.50, 75.00, '2026-10-22', '2026-10-16'),
(5, 'Software Engineer', 9.00, 8.00, 80.00, '2026-10-25', '2026-10-18'),
(6, 'Cloud Support Associate', 10.00, 8.00, 80.00, '2026-10-28', '2026-10-20'),
(7, 'Software Engineer', 12.00, 8.50, 85.00, '2026-11-01', '2026-10-24');

SELECT * FROM placement_drives;

CREATE TABLE placement_applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    drive_id INT NOT NULL,
    application_date DATE,
    application_status VARCHAR(30) DEFAULT 'Applied',
    selection_status VARCHAR(30) DEFAULT 'Pending',

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (drive_id)
        REFERENCES placement_drives(drive_id),

    UNIQUE(student_id, drive_id)
);

INSERT INTO placement_applications
(student_id, drive_id, application_date, application_status, selection_status)
VALUES
(1, 1, '2026-10-05', 'Applied', 'Pending'),
(1, 3, '2026-10-06', 'Applied', 'Selected'),
(1, 5, '2026-10-07', 'Applied', 'Pending'),
(2, 1, '2026-10-05', 'Applied', 'Rejected'),
(2, 2, '2026-10-06', 'Applied', 'Pending'),
(3, 2, '2026-10-06', 'Applied', 'Selected'),
(4, 4, '2026-10-07', 'Applied', 'Pending');

SELECT * FROM placement_applications;

SELECT
    s.student_name,
    c.company_name,
    pd.job_role,
    pd.package_lpa,
    pa.application_status,
    pa.selection_status
FROM placement_applications pa
JOIN students s
    ON pa.student_id = s.student_id
JOIN placement_drives pd
    ON pa.drive_id = pd.drive_id
JOIN companies c
    ON pd.company_id = c.company_id;


SELECT
    s.student_name,
    c.company_name,
    pd.job_role,
    pd.package_lpa
FROM placement_applications pa
JOIN students s
    ON pa.student_id = s.student_id
JOIN placement_drives pd
    ON pa.drive_id = pd.drive_id
JOIN companies c
    ON pd.company_id = c.company_id
WHERE pa.selection_status = 'Selected';

SELECT
    MAX(package_lpa) AS highest_package
FROM placement_drives;


CREATE VIEW student_academic_summary AS
SELECT
    s.student_id,
    s.register_number,
    s.student_name,
    d.department_name,
    c.course_code,
    c.course_name,
    a.attendance_percentage,
    r.marks,
    r.grade
FROM students s
JOIN departments d
    ON s.department_id = d.department_id
JOIN enrollments e
    ON s.student_id = e.student_id
JOIN courses c
    ON e.course_id = c.course_id
LEFT JOIN attendance a
    ON s.student_id = a.student_id
    AND c.course_id = a.course_id
LEFT JOIN results r
    ON s.student_id = r.student_id
    AND c.course_id = r.course_id;


SELECT * FROM student_academic_summary;

CREATE VIEW student_placement_status AS
SELECT
    s.register_number,
    s.student_name,
    co.company_name,
    pd.job_role,
    pd.package_lpa,
    pa.application_status,
    pa.selection_status
FROM placement_applications pa
JOIN students s
    ON pa.student_id = s.student_id
JOIN placement_drives pd
    ON pa.drive_id = pd.drive_id
JOIN companies co
    ON pd.company_id = co.company_id;

SELECT * FROM student_placement_status;

CREATE VIEW room_booking_details AS
SELECT
    rb.booking_id,
    cl.room_number,
    cl.building,
    f.faculty_name,
    rb.booking_date,
    rb.start_time,
    rb.end_time,
    rb.purpose,
    rb.booking_status
FROM room_bookings rb
JOIN classrooms cl
    ON rb.classroom_id = cl.classroom_id
LEFT JOIN faculty f
    ON rb.faculty_id = f.faculty_id;

SELECT * FROM room_booking_details;   

USE campussphere;

DROP PROCEDURE IF EXISTS GetStudentAcademicDetails;

CREATE PROCEDURE GetStudentAcademicDetails(IN p_student_id INT)
SELECT
    s.register_number,
    s.student_name,
    c.course_code,
    c.course_name,
    a.attendance_percentage,
    r.marks,
    r.grade
FROM students s
JOIN enrollments e
    ON s.student_id = e.student_id
JOIN courses c
    ON e.course_id = c.course_id
LEFT JOIN attendance a
    ON s.student_id = a.student_id
    AND c.course_id = a.course_id
LEFT JOIN results r
    ON s.student_id = r.student_id
    AND c.course_id = r.course_id
WHERE s.student_id = p_student_id;

CALL GetStudentAcademicDetails(1);


USE campussphere;

DROP PROCEDURE IF EXISTS GetLowAttendanceStudents;

CREATE PROCEDURE GetLowAttendanceStudents(IN p_min_attendance DECIMAL(5,2))
SELECT
    s.register_number,
    s.student_name,
    c.course_code,
    c.course_name,
    a.attendance_percentage
FROM attendance a
JOIN students s
    ON a.student_id = s.student_id
JOIN courses c
    ON a.course_id = c.course_id
WHERE a.attendance_percentage < p_min_attendance
ORDER BY a.attendance_percentage ASC;

CALL GetLowAttendanceStudents(75.00);

USE campussphere;

DROP PROCEDURE IF EXISTS GetStudentPlacementDetails;

CREATE PROCEDURE GetStudentPlacementDetails(IN p_student_id INT)
SELECT
    s.register_number,
    s.student_name,
    co.company_name,
    pd.job_role,
    pd.package_lpa,
    pa.application_status,
    pa.selection_status
FROM placement_applications pa
JOIN students s
    ON pa.student_id = s.student_id
JOIN placement_drives pd
    ON pa.drive_id = pd.drive_id
JOIN companies co
    ON pd.company_id = co.company_id
WHERE s.student_id = p_student_id;

CALL GetStudentPlacementDetails(1);

USE campussphere;

DROP FUNCTION IF EXISTS CalculateAttendance;

CREATE FUNCTION CalculateAttendance(
    p_total_classes INT,
    p_classes_attended INT
)
RETURNS DECIMAL(5,2)
DETERMINISTIC
RETURN
    CASE
        WHEN p_total_classes = 0 THEN 0.00
        ELSE (p_classes_attended / p_total_classes) * 100
    END;

SELECT CalculateAttendance(40, 36);

SELECT CalculateAttendance(40, 28);

USE campussphere;

DROP FUNCTION IF EXISTS CalculateGrade;

CREATE FUNCTION CalculateGrade(
    p_marks DECIMAL(5,2)
)
RETURNS VARCHAR(5)
DETERMINISTIC
RETURN
    CASE
        WHEN p_marks >= 90 THEN 'O'
        WHEN p_marks >= 80 THEN 'A+'
        WHEN p_marks >= 70 THEN 'A'
        WHEN p_marks >= 60 THEN 'B+'
        WHEN p_marks >= 50 THEN 'B'
        WHEN p_marks >= 40 THEN 'C'
        ELSE 'F'
    END;

SELECT CalculateGrade(95); 
SELECT CalculateGrade(85);
SELECT CalculateGrade(68);   


SELECT
    s.student_name,
    c.course_name,
    a.total_classes,
    a.classes_attended,
    CalculateAttendance(
        a.total_classes,
        a.classes_attended
    ) AS calculated_attendance,
    r.marks,
    CalculateGrade(r.marks) AS calculated_grade
FROM students s
JOIN attendance a
    ON s.student_id = a.student_id
JOIN courses c
    ON a.course_id = c.course_id
LEFT JOIN results r
    ON s.student_id = r.student_id
    AND c.course_id = r.course_id;

USE campussphere;

DROP TRIGGER IF EXISTS before_attendance_insert;

CREATE TRIGGER before_attendance_insert
BEFORE INSERT ON attendance
FOR EACH ROW
SET NEW.attendance_percentage =
    CASE
        WHEN NEW.total_classes = 0 THEN 0.00
        ELSE (NEW.classes_attended / NEW.total_classes) * 100
    END;    

INSERT INTO attendance
(student_id, course_id, total_classes, classes_attended)
VALUES
(4, 6, 40, 36);    

SELECT *
FROM attendance
WHERE student_id = 4
AND course_id = 6;

USE campussphere;

DROP TRIGGER IF EXISTS before_result_insert;

CREATE TRIGGER before_result_insert
BEFORE INSERT ON results
FOR EACH ROW
SET NEW.grade =
    CASE
        WHEN NEW.marks >= 90 THEN 'O'
        WHEN NEW.marks >= 80 THEN 'A+'
        WHEN NEW.marks >= 70 THEN 'A'
        WHEN NEW.marks >= 60 THEN 'B+'
        WHEN NEW.marks >= 50 THEN 'B'
        WHEN NEW.marks >= 40 THEN 'C'
        ELSE 'F'
    END;

INSERT INTO results
(student_id, course_id, exam_id, marks)
VALUES
(4, 5, 2, 87);    

SELECT *
FROM results
WHERE student_id = 4
AND course_id = 5;

USE campussphere;

DROP TRIGGER IF EXISTS equipment_maintenance_trigger;

CREATE TRIGGER equipment_maintenance_trigger
AFTER UPDATE ON equipment
FOR EACH ROW
INSERT INTO maintenance
(
    equipment_id,
    reported_date,
    problem_description,
    assigned_to,
    maintenance_status
)
SELECT
    NEW.equipment_id,
    CURDATE(),
    'Equipment automatically marked for maintenance',
    'Technical Team',
    'Pending'
WHERE OLD.status <> 'Under Maintenance'
  AND NEW.status = 'Under Maintenance';

  UPDATE equipment
SET status = 'Under Maintenance'
WHERE equipment_id = 2;

SELECT *
FROM maintenance
WHERE equipment_id = 2
ORDER BY maintenance_id DESC;

USE campussphere;

CREATE INDEX idx_student_department
ON students(department_id);

CREATE INDEX idx_course_department
ON courses(department_id);

CREATE INDEX idx_attendance_student
ON attendance(student_id);

CREATE INDEX idx_placement_student
ON placement_applications(student_id);

SHOW INDEX FROM students;

SHOW INDEX FROM attendance;

EXPLAIN
SELECT *
FROM attendance
WHERE student_id = 1;

USE campussphere;

SELECT *
FROM room_bookings;

START TRANSACTION;

INSERT INTO room_bookings
(
    classroom_id,
    faculty_id,
    booking_date,
    start_time,
    end_time,
    purpose,
    booking_status
)
VALUES
(
    3,
    1,
    '2026-10-08',
    '10:00:00',
    '12:00:00',
    'DBMS Project Review',
    'Confirmed'
);

SELECT *
FROM room_bookings
WHERE booking_date = '2026-10-08';

COMMIT;
use campussphere;
SELECT *
FROM room_bookings
WHERE booking_date = '2026-10-08';

START TRANSACTION;

INSERT INTO room_bookings
(
    classroom_id,
    faculty_id,
    booking_date,
    start_time,
    end_time,
    purpose,
    booking_status
)
VALUES
(
    2,
    2,
    '2026-10-09',
    '14:00:00',
    '16:00:00',
    'Temporary Seminar Booking',
    'Confirmed'
);

SELECT *
FROM room_bookings
WHERE booking_date = '2026-10-09';

ROLLBACK;

SELECT *
FROM room_bookings
WHERE booking_date = '2026-10-09';

USE campussphere;

CREATE TABLE IF NOT EXISTS complaint_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);
USE campussphere;

CREATE TABLE complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    category_id INT NOT NULL,
    complaint_title VARCHAR(150) NOT NULL,
    complaint_description VARCHAR(500),
    priority VARCHAR(20) DEFAULT 'Medium',
    complaint_date DATE NOT NULL,
    assigned_to VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Pending',
    resolution VARCHAR(500),
    resolved_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (category_id) REFERENCES complaint_categories(category_id)
);
USE campussphere;

SHOW TABLES LIKE 'complaints';

INSERT INTO complaint_categories
(category_name, description)
VALUES
('Academic', 'Academic related complaints'),
('Infrastructure', 'Building and infrastructure complaints'),
('IT Support', 'Computer, network and technical complaints'),
('Hostel', 'Hostel related complaints'),
('Transport', 'Transport related complaints'),
('Other', 'Other campus related complaints');

USE campussphere;

INSERT INTO complaints
(
    student_id,
    category_id,
    complaint_title,
    complaint_description,
    priority,
    complaint_date,
    assigned_to,
    status,
    resolution,
    resolved_date
)
VALUES
(
    1,
    3,
    'Wi-Fi not working',
    'Unable to connect to campus Wi-Fi in the laboratory.',
    'High',
    '2026-09-25',
    'IT Support',
    'In Progress',
    NULL,
    NULL
),
(
    2,
    2,
    'Projector issue',
    'Projector in the classroom is not displaying properly.',
    'Medium',
    '2026-09-26',
    'Technical Team',
    'Pending',
    NULL,
    NULL
),
(
    3,
    1,
    'Exam timetable clarification',
    'Request for clarification regarding examination schedule.',
    'Low',
    '2026-09-27',
    'Academic Office',
    'Resolved',
    'Exam timetable clarification provided.',
    '2026-09-28'
);

USE campussphere;

SHOW PROCESSLIST;

SHOW PROCESSLIST;

USE campussphere;

SHOW TABLES LIKE 'complaints';

CREATE TABLE complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    category_id INT NOT NULL,
    complaint_title VARCHAR(150) NOT NULL,
    complaint_description VARCHAR(500),
    priority VARCHAR(20) DEFAULT 'Medium',
    complaint_date DATE NOT NULL,
    assigned_to VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Pending',
    resolution VARCHAR(500),
    resolved_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (category_id) REFERENCES complaint_categories(category_id)
);

USE campussphere;

SELECT * FROM complaints;

SELECT
    c.complaint_id,
    s.student_name,
    cc.category_name,
    c.complaint_title,
    c.priority,
    c.status
FROM complaints c
JOIN students s
    ON c.student_id = s.student_id
JOIN complaint_categories cc
    ON c.category_id = cc.category_id;

USE campussphere;

SELECT * FROM results;    


SELECT
    r.result_id,
    s.register_number,
    s.student_name,
    c.course_code,
    c.course_name,
    e.exam_name,
    e.exam_date,
    r.marks,
    r.grade
FROM results r
JOIN students s
    ON r.student_id = s.student_id
JOIN courses c
    ON r.course_id = c.course_id
JOIN exams e
    ON r.exam_id = e.exam_id
ORDER BY s.student_id, e.exam_date;

USE campussphere;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
);

INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'Admin'),
('faculty1', 'faculty123', 'Faculty'),
('student1', 'student123', 'Student');

SELECT * FROM users;

USE campussphere;

ALTER TABLE users
ADD COLUMN student_id INT NULL,
ADD CONSTRAINT fk_users_student
FOREIGN KEY (student_id)
REFERENCES students(student_id);

UPDATE users
SET student_id = 1
WHERE username = 'student1';

ALTER TABLE users
ADD COLUMN faculty_id INT NULL,
ADD CONSTRAINT fk_users_faculty
FOREIGN KEY (faculty_id)
REFERENCES faculty(faculty_id);

UPDATE users
SET faculty_id = 1
WHERE username = 'faculty1';

SELECT
    user_id,
    username,
    role,
    student_id,
    faculty_id
FROM users;

USE campussphere;

SELECT
    user_id,
    username,
    role,
    student_id,
    faculty_id
FROM users;

USE campussphere;

SHOW FULL TABLES
WHERE TABLE_TYPE = 'VIEW';

SHOW PROCEDURE STATUS
WHERE Db = 'campussphere';

SHOW FUNCTION STATUS
WHERE Db = 'campussphere';

SHOW FUNCTION STATUS
WHERE Db = 'campussphere';