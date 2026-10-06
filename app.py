from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from functools import wraps
from datetime import date


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = "campussphere-secret-key"


# ============================================================
# MYSQL CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",

    # CHANGE THIS
    "password": "Mysql@123",

    "database": "campussphere"
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )


# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login to continue.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# ROLE REQUIRED DECORATOR
# ============================================================

def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:

                flash(
                    "Please login to continue.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            if session.get("role") not in allowed_roles:

                return render_template(
                    "error.html",
                    error_code=403,
                    error_message="You do not have permission to access this page."
                ), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def fetch_all(query, params=()):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            query,
            params
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


def fetch_one(query, params=()):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            query,
            params
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return render_template(
                "login.html"
            )

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    user_id,
                    username,
                    password,
                    role,
                    student_id,
                    faculty_id
                FROM users
                WHERE username = %s
                  AND password = %s
                """,
                (
                    username,
                    password
                )
            )

            user = cursor.fetchone()

        finally:

            cursor.close()
            connection.close()


        if user:

            session.clear()

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["student_id"] = user["student_id"]
            session["faculty_id"] = user["faculty_id"]

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
@login_required
def dashboard():

    role = session.get("role")


    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    if role == "Admin":

        total_students = fetch_one(
            "SELECT COUNT(*) AS count FROM students"
        )["count"]

        total_faculty = fetch_one(
            "SELECT COUNT(*) AS count FROM faculty"
        )["count"]

        total_courses = fetch_one(
            "SELECT COUNT(*) AS count FROM courses"
        )["count"]

        total_drives = fetch_one(
            "SELECT COUNT(*) AS count FROM placement_drives"
        )["count"]

        pending_complaints = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM complaints
            WHERE status = 'Pending'
            """
        )["count"]

        total_bookings = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM room_bookings
            """
        )["count"]


        return render_template(
            "index.html",

            role=role,

            total_students=total_students,
            total_faculty=total_faculty,
            total_courses=total_courses,
            total_drives=total_drives,

            pending_complaints=pending_complaints,
            total_bookings=total_bookings
        )


    # ========================================================
    # FACULTY DASHBOARD
    # ========================================================

    if role == "Faculty":

        faculty_id = session.get(
            "faculty_id"
        )

        faculty = fetch_one(
            """
            SELECT
                f.*,
                d.department_name
            FROM faculty f
            LEFT JOIN departments d
                ON f.department_id = d.department_id
            WHERE f.faculty_id = %s
            """,
            (faculty_id,)
        )


        my_courses = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM courses
            WHERE faculty_id = %s
            """,
            (faculty_id,)
        )["count"]


        my_bookings = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM room_bookings
            WHERE faculty_id = %s
            """,
            (faculty_id,)
        )["count"]


        pending_complaints = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM complaints
            WHERE status = 'Pending'
            """
        )["count"]


        return render_template(
            "index.html",

            role=role,

            faculty=faculty,

            my_courses=my_courses,
            my_bookings=my_bookings,
            pending_complaints=pending_complaints
        )


    # ========================================================
    # STUDENT DASHBOARD
    # ========================================================

    if role == "Student":

        student_id = session.get(
            "student_id"
        )


        student = fetch_one(
            """
            SELECT
                s.*,
                d.department_name
            FROM students s
            LEFT JOIN departments d
                ON s.department_id = d.department_id
            WHERE s.student_id = %s
            """,
            (student_id,)
        )


        attendance_result = fetch_one(
            """
            SELECT
                COALESCE(
                    AVG(attendance_percentage),
                    0
                ) AS average_attendance
            FROM attendance
            WHERE student_id = %s
            """,
            (student_id,)
        )


        enrolled_courses = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM enrollments
            WHERE student_id = %s
            """,
            (student_id,)
        )["count"]


        placement_applications = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM placement_applications
            WHERE student_id = %s
            """,
            (student_id,)
        )["count"]


        complaints = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM complaints
            WHERE student_id = %s
            """,
            (student_id,)
        )["count"]


        return render_template(
            "index.html",

            role=role,

            student=student,

            average_attendance=
                round(
                    float(
                        attendance_result[
                            "average_attendance"
                        ]
                    ),
                    2
                ),

            enrolled_courses=enrolled_courses,

            placement_applications=
                placement_applications,

            complaints=complaints
        )


    return render_template(
        "index.html",
        role=role
    )


# ============================================================
# STUDENTS
# ============================================================

@app.route("/students")
@role_required("Admin", "Faculty")
def students():

    students_list = fetch_all(
        """
        SELECT
            s.*,
            d.department_name
        FROM students s
        LEFT JOIN departments d
            ON s.department_id = d.department_id
        ORDER BY s.student_id
        """
    )


    departments = fetch_all(
        """
        SELECT
            department_id,
            department_name
        FROM departments
        ORDER BY department_name
        """
    )


    return render_template(
        "students.html",

        students=students_list,
        departments=departments,

        role=session.get("role")
    )


# ============================================================
# ADD STUDENT
# ============================================================

@app.route(
    "/students/add",
    methods=["POST"]
)
@role_required("Admin")
def add_student():

    register_number = request.form.get(
        "register_number",
        ""
    ).strip()

    student_name = request.form.get(
        "student_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    date_of_birth = request.form.get(
        "date_of_birth"
    ) or None

    gender = request.form.get(
        "gender",
        ""
    ).strip()

    year_of_study = request.form.get(
        "year_of_study"
    ) or None

    section = request.form.get(
        "section",
        ""
    ).strip()

    department_id = request.form.get(
        "department_id"
    ) or None


    if not register_number or not student_name:

        flash(
            "Register number and student name are required.",
            "error"
        )

        return redirect(
            url_for("students")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO students
            (
                register_number,
                student_name,
                email,
                phone,
                date_of_birth,
                gender,
                year_of_study,
                section,
                department_id
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                register_number,
                student_name,
                email or None,
                phone or None,
                date_of_birth,
                gender or None,
                year_of_study,
                section or None,
                department_id
            )
        )

        connection.commit()

        flash(
            "Student added successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to add student: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("students")
    )


# ============================================================
# DELETE STUDENT
# ============================================================

@app.route(
    "/students/delete/<int:student_id>",
    methods=["POST"]
)
@role_required("Admin")
def delete_student(student_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        connection.commit()

        flash(
            "Student deleted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to delete student: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("students")
    )


# ============================================================
# ATTENDANCE
# ============================================================

@app.route("/attendance")
@login_required
def attendance():

    role = session.get("role")


    if role == "Student":

        student_id = session.get(
            "student_id"
        )

        attendance_data = fetch_all(
            """
            SELECT
                a.*,
                s.register_number,
                s.student_name,
                c.course_code,
                c.course_name
            FROM attendance a

            JOIN students s
                ON a.student_id = s.student_id

            JOIN courses c
                ON a.course_id = c.course_id

            WHERE a.student_id = %s

            ORDER BY c.course_code
            """,
            (student_id,)
        )


        students_list = []

        courses_list = []


    else:

        if role == "Faculty":

            attendance_data = fetch_all(
                """
                SELECT
                    a.*,
                    s.register_number,
                    s.student_name,
                    c.course_code,
                    c.course_name
                FROM attendance a

                JOIN students s
                    ON a.student_id = s.student_id

                JOIN courses c
                    ON a.course_id = c.course_id

                WHERE c.faculty_id = %s

                ORDER BY
                    s.register_number,
                    c.course_code
                """,
                (
                    session.get(
                        "faculty_id"
                    ),
                )
            )

            courses_list = fetch_all(
                """
                SELECT
                    course_id,
                    course_code,
                    course_name
                FROM courses
                WHERE faculty_id = %s
                ORDER BY course_code
                """,
                (
                    session.get(
                        "faculty_id"
                    ),
                )
            )

        else:

            attendance_data = fetch_all(
                """
                SELECT
                    a.*,
                    s.register_number,
                    s.student_name,
                    c.course_code,
                    c.course_name
                FROM attendance a

                JOIN students s
                    ON a.student_id = s.student_id

                JOIN courses c
                    ON a.course_id = c.course_id

                ORDER BY
                    s.register_number,
                    c.course_code
                """
            )

            courses_list = fetch_all(
                """
                SELECT
                    course_id,
                    course_code,
                    course_name
                FROM courses
                ORDER BY course_code
                """
            )


        students_list = fetch_all(
            """
            SELECT
                student_id,
                register_number,
                student_name
            FROM students
            ORDER BY register_number
            """
        )


    return render_template(
        "attendance.html",

        attendance=attendance_data,
        students=students_list,
        courses=courses_list,
        role=role
    )


# ============================================================
# ADD ATTENDANCE
# ============================================================

@app.route(
    "/attendance/add",
    methods=["POST"]
)
@login_required
def add_attendance():

    role = session.get("role")


    if role == "Student":

        student_id = session.get(
            "student_id"
        )

    else:

        student_id = request.form.get(
            "student_id"
        )


    course_id = request.form.get(
        "course_id"
    )

    total_classes = request.form.get(
        "total_classes"
    )

    classes_attended = request.form.get(
        "classes_attended"
    )


    try:

        total_classes = int(
            total_classes
        )

        classes_attended = int(
            classes_attended
        )

    except (TypeError, ValueError):

        flash(
            "Attendance values must be valid numbers.",
            "error"
        )

        return redirect(
            url_for("attendance")
        )


    if not student_id or not course_id:

        flash(
            "Student and course are required.",
            "error"
        )

        return redirect(
            url_for("attendance")
        )


    if total_classes <= 0:

        flash(
            "Total classes must be greater than zero.",
            "error"
        )

        return redirect(
            url_for("attendance")
        )


    if classes_attended < 0 or classes_attended > total_classes:

        flash(
            "Classes attended must be between 0 and total classes.",
            "error"
        )

        return redirect(
            url_for("attendance")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        if role == "Faculty":

            course_check = fetch_one(
                """
                SELECT course_id
                FROM courses
                WHERE course_id = %s
                  AND faculty_id = %s
                """,
                (
                    course_id,
                    session.get(
                        "faculty_id"
                    )
                )
            )

            if not course_check:

                flash(
                    "You can only add attendance for your courses.",
                    "error"
                )

                return redirect(
                    url_for("attendance")
                )


        cursor.execute(
            """
            INSERT INTO attendance
            (
                student_id,
                course_id,
                total_classes,
                classes_attended
            )
            VALUES
            (
                %s, %s, %s, %s
            )
            """,
            (
                student_id,
                course_id,
                total_classes,
                classes_attended
            )
        )

        connection.commit()

        flash(
            "Attendance added successfully. Attendance percentage was calculated by the database trigger.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to add attendance: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("attendance")
    )


# ============================================================
# EXAMINATIONS
# ============================================================

@app.route("/examinations")
@login_required
def examinations():

    role = session.get("role")


    # ========================================================
    # EXAMS
    # ========================================================

    if role == "Student":

        student_id = session.get(
            "student_id"
        )

        exams = fetch_all(
            """
            SELECT
                e.*,
                c.course_code,
                c.course_name
            FROM exams e

            JOIN courses c
                ON e.course_id = c.course_id

            JOIN enrollments en
                ON en.course_id = c.course_id

            WHERE en.student_id = %s

            ORDER BY
                e.exam_date,
                e.start_time
            """,
            (student_id,)
        )

    elif role == "Faculty":

        exams = fetch_all(
            """
            SELECT
                e.*,
                c.course_code,
                c.course_name
            FROM exams e

            JOIN courses c
                ON e.course_id = c.course_id

            WHERE c.faculty_id = %s

            ORDER BY
                e.exam_date,
                e.start_time
            """,
            (
                session.get(
                    "faculty_id"
                ),
            )
        )

    else:

        exams = fetch_all(
            """
            SELECT
                e.*,
                c.course_code,
                c.course_name
            FROM exams e

            JOIN courses c
                ON e.course_id = c.course_id

            ORDER BY
                e.exam_date,
                e.start_time
            """
        )


    # ========================================================
    # RESULTS
    # ========================================================

    if role == "Student":

        results = fetch_all(
            """
            SELECT
                r.*,
                c.course_code,
                c.course_name,
                e.exam_name,
                e.exam_date
            FROM results r

            JOIN courses c
                ON r.course_id = c.course_id

            JOIN exams e
                ON r.exam_id = e.exam_id

            WHERE r.student_id = %s

            ORDER BY
                e.exam_date DESC
            """,
            (
                session.get(
                    "student_id"
                ),
            )
        )

    elif role == "Faculty":

        results = fetch_all(
            """
            SELECT
                r.*,
                s.register_number,
                s.student_name,
                c.course_code,
                c.course_name,
                e.exam_name,
                e.exam_date
            FROM results r

            JOIN students s
                ON r.student_id = s.student_id

            JOIN courses c
                ON r.course_id = c.course_id

            JOIN exams e
                ON r.exam_id = e.exam_id

            WHERE c.faculty_id = %s

            ORDER BY
                e.exam_date DESC
            """,
            (
                session.get(
                    "faculty_id"
                ),
            )
        )

    else:

        results = fetch_all(
            """
            SELECT
                r.*,
                s.register_number,
                s.student_name,
                c.course_code,
                c.course_name,
                e.exam_name,
                e.exam_date
            FROM results r

            JOIN students s
                ON r.student_id = s.student_id

            JOIN courses c
                ON r.course_id = c.course_id

            JOIN exams e
                ON r.exam_id = e.exam_id

            ORDER BY
                e.exam_date DESC
            """
        )


    # ========================================================
    # REGISTRATIONS
    # ========================================================

    if role == "Student":

        registrations = fetch_all(
            """
            SELECT
                er.*,
                e.exam_name,
                e.exam_date,
                e.start_time,
                e.end_time,
                e.room_number,
                c.course_code,
                c.course_name
            FROM exam_registrations er

            JOIN exams e
                ON er.exam_id = e.exam_id

            JOIN courses c
                ON e.course_id = c.course_id

            WHERE er.student_id = %s

            ORDER BY
                e.exam_date
            """,
            (
                session.get(
                    "student_id"
                ),
            )
        )

    else:

        registrations = fetch_all(
            """
            SELECT
                er.*,
                s.register_number,
                s.student_name,
                e.exam_name,
                e.exam_date,
                c.course_code,
                c.course_name
            FROM exam_registrations er

            JOIN students s
                ON er.student_id = s.student_id

            JOIN exams e
                ON er.exam_id = e.exam_id

            JOIN courses c
                ON e.course_id = c.course_id

            ORDER BY
                e.exam_date
            """
        )


    # ========================================================
    # COURSES
    # ========================================================

    if role == "Faculty":

        courses = fetch_all(
            """
            SELECT
                course_id,
                course_code,
                course_name
            FROM courses
            WHERE faculty_id = %s
            ORDER BY course_code
            """,
            (
                session.get(
                    "faculty_id"
                ),
            )
        )

    elif role == "Student":

        courses = fetch_all(
            """
            SELECT
                c.course_id,
                c.course_code,
                c.course_name
            FROM courses c

            JOIN enrollments e
                ON c.course_id = e.course_id

            WHERE e.student_id = %s

            ORDER BY c.course_code
            """,
            (
                session.get(
                    "student_id"
                ),
            )
        )

    else:

        courses = fetch_all(
            """
            SELECT
                course_id,
                course_code,
                course_name
            FROM courses
            ORDER BY course_code
            """
        )


    # ========================================================
    # STUDENTS
    # ========================================================

    if role == "Student":

        students_list = []

    else:

        students_list = fetch_all(
            """
            SELECT
                student_id,
                register_number,
                student_name
            FROM students
            ORDER BY register_number
            """
        )


    return render_template(
        "examinations.html",

        exams=exams,
        results=results,
        registrations=registrations,
        courses=courses,
        students=students_list,

        role=role
    )


# ============================================================
# ADD EXAM
# ============================================================

@app.route(
    "/examinations/add",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def add_exam():

    course_id = request.form.get(
        "course_id"
    )

    exam_name = request.form.get(
        "exam_name",
        ""
    ).strip()

    exam_date = request.form.get(
        "exam_date"
    )

    start_time = request.form.get(
        "start_time"
    ) or None

    end_time = request.form.get(
        "end_time"
    ) or None

    room_number = request.form.get(
        "room_number",
        ""
    ).strip()


    if not course_id or not exam_name or not exam_date:

        flash(
            "Course, exam name and exam date are required.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    if session.get("role") == "Faculty":

        course_check = fetch_one(
            """
            SELECT course_id
            FROM courses
            WHERE course_id = %s
              AND faculty_id = %s
            """,
            (
                course_id,
                session.get(
                    "faculty_id"
                )
            )
        )

        if not course_check:

            flash(
                "You can only create exams for your courses.",
                "error"
            )

            return redirect(
                url_for("examinations")
            )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO exams
            (
                course_id,
                exam_name,
                exam_date,
                start_time,
                end_time,
                room_number
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                course_id,
                exam_name,
                exam_date,
                start_time,
                end_time,
                room_number or None
            )
        )

        connection.commit()

        flash(
            "Exam added successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to add exam: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("examinations")
    )


# ============================================================
# REGISTER FOR EXAM
# ============================================================

@app.route(
    "/examinations/register",
    methods=["POST"]
)
@role_required("Student")
def register_exam():

    exam_id = request.form.get(
        "exam_id"
    )

    student_id = session.get(
        "student_id"
    )


    if not exam_id:

        flash(
            "Exam is required.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    exam_check = fetch_one(
        """
        SELECT
            e.exam_id
        FROM exams e

        JOIN enrollments en
            ON e.course_id = en.course_id

        WHERE e.exam_id = %s
          AND en.student_id = %s
        """,
        (
            exam_id,
            student_id
        )
    )


    if not exam_check:

        flash(
            "You can only register for an exam belonging to an enrolled course.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO exam_registrations
            (
                student_id,
                exam_id,
                registration_date
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                student_id,
                exam_id,
                date.today()
            )
        )

        connection.commit()

        flash(
            "Exam registration completed.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to register for exam: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("examinations")
    )


# ============================================================
# ADD RESULT
# ============================================================

@app.route(
    "/examinations/result/add",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def add_result():

    student_id = request.form.get(
        "student_id"
    )

    course_id = request.form.get(
        "course_id"
    )

    exam_id = request.form.get(
        "exam_id"
    )

    marks = request.form.get(
        "marks"
    )


    if not student_id or not course_id or not exam_id or not marks:

        flash(
            "Student, course, exam and marks are required.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    try:

        marks = float(
            marks
        )

    except ValueError:

        flash(
            "Marks must be a valid number.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    if marks < 0 or marks > 100:

        flash(
            "Marks must be between 0 and 100.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    exam_check = fetch_one(
        """
        SELECT
            e.exam_id,
            e.course_id
        FROM exams e
        WHERE e.exam_id = %s
          AND e.course_id = %s
        """,
        (
            exam_id,
            course_id
        )
    )


    if not exam_check:

        flash(
            "Selected exam does not belong to the selected course.",
            "error"
        )

        return redirect(
            url_for("examinations")
        )


    if session.get("role") == "Faculty":

        course_check = fetch_one(
            """
            SELECT course_id
            FROM courses
            WHERE course_id = %s
              AND faculty_id = %s
            """,
            (
                course_id,
                session.get(
                    "faculty_id"
                )
            )
        )

        if not course_check:

            flash(
                "You can only add results for your courses.",
                "error"
            )

            return redirect(
                url_for("examinations")
            )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO results
            (
                student_id,
                course_id,
                exam_id,
                marks
            )
            VALUES
            (
                %s, %s, %s, %s
            )
            """,
            (
                student_id,
                course_id,
                exam_id,
                marks
            )
        )

        connection.commit()

        flash(
            "Result added successfully. Grade was calculated by the database trigger.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to add result: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("examinations")
    )


# ============================================================
# ROOM BOOKINGS
# ============================================================

@app.route("/room-bookings")
@role_required("Admin", "Faculty")
def room_bookings():

    role = session.get(
        "role"
    )


    if role == "Faculty":

        bookings = fetch_all(
            """
            SELECT
                rb.*,
                c.room_number,
                c.building,
                c.capacity,
                c.room_type,
                f.faculty_name
            FROM room_bookings rb

            JOIN classrooms c
                ON rb.classroom_id = c.classroom_id

            LEFT JOIN faculty f
                ON rb.faculty_id = f.faculty_id

            WHERE rb.faculty_id = %s

            ORDER BY
                rb.booking_date DESC,
                rb.start_time
            """,
            (
                session.get(
                    "faculty_id"
                ),
            )
        )

    else:

        bookings = fetch_all(
            """
            SELECT
                rb.*,
                c.room_number,
                c.building,
                c.capacity,
                c.room_type,
                f.faculty_name
            FROM room_bookings rb

            JOIN classrooms c
                ON rb.classroom_id = c.classroom_id

            LEFT JOIN faculty f
                ON rb.faculty_id = f.faculty_id

            ORDER BY
                rb.booking_date DESC,
                rb.start_time
            """
        )


    classrooms = fetch_all(
        """
        SELECT
            classroom_id,
            room_number,
            building,
            capacity,
            room_type,
            availability_status
        FROM classrooms
        ORDER BY room_number
        """
    )


    faculty_list = fetch_all(
        """
        SELECT
            faculty_id,
            faculty_name
        FROM faculty
        ORDER BY faculty_name
        """
    )


    return render_template(
        "room_bookings.html",

        bookings=bookings,
        classrooms=classrooms,
        faculty=faculty_list,

        role=role
    )


# ============================================================
# ADD ROOM BOOKING
# ============================================================

@app.route(
    "/room-bookings/add",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def add_room_booking():

    role = session.get(
        "role"
    )


    classroom_id = request.form.get(
        "classroom_id"
    )

    booking_date = request.form.get(
        "booking_date"
    )

    start_time = request.form.get(
        "start_time"
    )

    end_time = request.form.get(
        "end_time"
    )

    purpose = request.form.get(
        "purpose",
        ""
    ).strip()


    if role == "Faculty":

        faculty_id = session.get(
            "faculty_id"
        )

    else:

        faculty_id = request.form.get(
            "faculty_id"
        ) or None


    if not classroom_id or not booking_date or not start_time or not end_time:

        flash(
            "Room, date, start time and end time are required.",
            "error"
        )

        return redirect(
            url_for("room_bookings")
        )


    if start_time >= end_time:

        flash(
            "End time must be later than start time.",
            "error"
        )

        return redirect(
            url_for("room_bookings")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # ====================================================
        # CONFLICT CHECK
        # ====================================================

        cursor.execute(
            """
            SELECT booking_id
            FROM room_bookings

            WHERE classroom_id = %s
              AND booking_date = %s

              AND booking_status <> 'Cancelled'

              AND start_time < %s
              AND end_time > %s
            """,
            (
                classroom_id,
                booking_date,
                end_time,
                start_time
            )
        )

        conflict = cursor.fetchone()


        if conflict:

            connection.rollback()

            flash(
                "Room booking conflict detected. The room is already booked for the selected time.",
                "error"
            )

            return redirect(
                url_for("room_bookings")
            )


        # ====================================================
        # TRANSACTION INSERT
        # ====================================================

        cursor.execute(
            """
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
                %s, %s, %s, %s, %s, %s, 'Confirmed'
            )
            """,
            (
                classroom_id,
                faculty_id,
                booking_date,
                start_time,
                end_time,
                purpose or None
            )
        )


        connection.commit()

        flash(
            "Room booking created successfully and committed.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to create booking: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("room_bookings")
    )


# ============================================================
# UPDATE ROOM BOOKING
# ============================================================

@app.route(
    "/room-bookings/update/<int:booking_id>",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def update_room_booking(booking_id):

    role = session.get(
        "role"
    )


    booking = fetch_one(
        """
        SELECT *
        FROM room_bookings
        WHERE booking_id = %s
        """,
        (booking_id,)
    )


    if not booking:

        flash(
            "Booking not found.",
            "error"
        )

        return redirect(
            url_for("room_bookings")
        )


    if (
        role == "Faculty"
        and booking["faculty_id"]
        != session.get("faculty_id")
    ):

        flash(
            "You can only update your own bookings.",
            "error"
        )

        return redirect(
            url_for("room_bookings")
        )


    booking_status = request.form.get(
        "booking_status",
        "Confirmed"
    )


    purpose = request.form.get(
        "purpose",
        ""
    ).strip()


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE room_bookings
            SET
                booking_status = %s,
                purpose = %s
            WHERE booking_id = %s
            """,
            (
                booking_status,
                purpose or None,
                booking_id
            )
        )

        connection.commit()

        flash(
            "Room booking updated successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to update booking: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("room_bookings")
    )


# ============================================================
# DELETE ROOM BOOKING
# ============================================================

@app.route(
    "/room-bookings/delete/<int:booking_id>",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def delete_room_booking(booking_id):

    role = session.get(
        "role"
    )


    booking = fetch_one(
        """
        SELECT *
        FROM room_bookings
        WHERE booking_id = %s
        """,
        (booking_id,)
    )


    if not booking:

        flash(
            "Booking not found.",
            "error"
        )

        return redirect(
            url_for("room_bookings")
        )


    if (
        role == "Faculty"
        and booking["faculty_id"]
        != session.get("faculty_id")
    ):

        flash(
            "You can only delete your own bookings.",
            "error"
        )

        return redirect(
            url_for("room_bookings")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM room_bookings
            WHERE booking_id = %s
            """,
            (booking_id,)
        )

        connection.commit()

        flash(
            "Room booking deleted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to delete booking: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("room_bookings")
    )


# ============================================================
# PLACEMENTS
# ============================================================

@app.route("/placements")
@login_required
def placements():

    role = session.get(
        "role"
    )


    # ========================================================
    # DRIVES
    # ========================================================

    drives = fetch_all(
        """
        SELECT
            pd.*,
            c.company_name,
            c.industry,
            c.location,
            c.website

        FROM placement_drives pd

        JOIN companies c
            ON pd.company_id = c.company_id

        ORDER BY
            pd.drive_date,
            c.company_name
        """
    )


    # ========================================================
    # APPLICATIONS
    # ========================================================

    if role == "Student":

        applications = fetch_all(
            """
            SELECT
                pa.*,

                pd.job_role,
                pd.package_lpa,

                c.company_name

            FROM placement_applications pa

            JOIN placement_drives pd
                ON pa.drive_id = pd.drive_id

            JOIN companies c
                ON pd.company_id = c.company_id

            WHERE pa.student_id = %s

            ORDER BY
                pa.application_date DESC
            """,
            (
                session.get(
                    "student_id"
                ),
            )
        )

    else:

        applications = fetch_all(
            """
            SELECT
                pa.*,

                s.register_number,
                s.student_name,

                pd.job_role,
                pd.package_lpa,

                c.company_name

            FROM placement_applications pa

            JOIN students s
                ON pa.student_id = s.student_id

            JOIN placement_drives pd
                ON pa.drive_id = pd.drive_id

            JOIN companies c
                ON pd.company_id = c.company_id

            ORDER BY
                pa.application_date DESC
            """
        )


    # ========================================================
    # COMPANIES
    # ========================================================

    companies = fetch_all(
        """
        SELECT
            company_id,
            company_name
        FROM companies
        ORDER BY company_name
        """
    )


    return render_template(
        "placements.html",

        drives=drives,
        applications=applications,
        companies=companies,

        role=role
    )


# ============================================================
# ADD PLACEMENT DRIVE
# ============================================================

@app.route(
    "/placements/drive/add",
    methods=["POST"]
)
@role_required("Admin")
def add_placement_drive():

    company_id = request.form.get(
        "company_id"
    )

    job_role = request.form.get(
        "job_role",
        ""
    ).strip()

    package_lpa = request.form.get(
        "package_lpa"
    ) or None

    minimum_cgpa = request.form.get(
        "minimum_cgpa"
    ) or None

    minimum_attendance = request.form.get(
        "minimum_attendance"
    ) or None

    drive_date = request.form.get(
        "drive_date"
    ) or None

    application_deadline = request.form.get(
        "application_deadline"
    ) or None


    if not company_id or not job_role:

        flash(
            "Company and job role are required.",
            "error"
        )

        return redirect(
            url_for("placements")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO placement_drives
            (
                company_id,
                job_role,
                package_lpa,
                minimum_cgpa,
                minimum_attendance,
                drive_date,
                application_deadline
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                company_id,
                job_role,
                package_lpa,
                minimum_cgpa,
                minimum_attendance,
                drive_date,
                application_deadline
            )
        )

        connection.commit()

        flash(
            "Placement drive added successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to add placement drive: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("placements")
    )


# ============================================================
# APPLY FOR PLACEMENT
# ============================================================

@app.route(
    "/placements/apply",
    methods=["POST"]
)
@role_required("Student")
def apply_placement():

    student_id = session.get(
        "student_id"
    )

    drive_id = request.form.get(
        "drive_id"
    )


    if not drive_id:

        flash(
            "Placement drive is required.",
            "error"
        )

        return redirect(
            url_for("placements")
        )


    drive = fetch_one(
        """
        SELECT
            drive_id,
            application_deadline
        FROM placement_drives
        WHERE drive_id = %s
        """,
        (drive_id,)
    )


    if not drive:

        flash(
            "Placement drive not found.",
            "error"
        )

        return redirect(
            url_for("placements")
        )


    # ========================================================
    # DEADLINE CHECK
    # ========================================================

    if drive["application_deadline"]:

        if date.today() > drive["application_deadline"]:

            flash(
                "The application deadline for this drive has passed.",
                "error"
            )

            return redirect(
                url_for("placements")
            )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO placement_applications
            (
                student_id,
                drive_id,
                application_date,
                application_status,
                selection_status
            )
            VALUES
            (
                %s, %s, %s, 'Applied', 'Pending'
            )
            """,
            (
                student_id,
                drive_id,
                date.today()
            )
        )

        connection.commit()

        flash(
            "Placement application submitted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to apply: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("placements")
    )


# ============================================================
# UPDATE PLACEMENT APPLICATION
# ============================================================

@app.route(
    "/placements/update/<int:application_id>",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def update_placement_application(application_id):

    selection_status = request.form.get(
        "selection_status"
    )


    if selection_status not in (
        "Pending",
        "Selected",
        "Rejected"
    ):

        flash(
            "Invalid selection status.",
            "error"
        )

        return redirect(
            url_for("placements")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE placement_applications

            SET selection_status = %s

            WHERE application_id = %s
            """,
            (
                selection_status,
                application_id
            )
        )

        connection.commit()

        flash(
            "Placement application updated successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to update application: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("placements")
    )


# ============================================================
# DELETE PLACEMENT APPLICATION
# ============================================================

@app.route(
    "/placements/delete/<int:application_id>",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def delete_placement_application(application_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM placement_applications
            WHERE application_id = %s
            """,
            (application_id,)
        )

        connection.commit()

        flash(
            "Placement application deleted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to delete application: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("placements")
    )


# ============================================================
# COMPLAINTS
# ============================================================

@app.route("/complaints")
@login_required
def complaints():

    role = session.get(
        "role"
    )


    # ========================================================
    # COMPLAINTS
    # ========================================================

    if role == "Student":

        complaints_data = fetch_all(
            """
            SELECT
                c.*,
                cc.category_name

            FROM complaints c

            JOIN complaint_categories cc
                ON c.category_id = cc.category_id

            WHERE c.student_id = %s

            ORDER BY
                c.complaint_date DESC,
                c.complaint_id DESC
            """,
            (
                session.get(
                    "student_id"
                ),
            )
        )

    else:

        complaints_data = fetch_all(
            """
            SELECT
                c.*,

                s.student_name,
                s.register_number,

                cc.category_name

            FROM complaints c

            JOIN students s
                ON c.student_id = s.student_id

            JOIN complaint_categories cc
                ON c.category_id = cc.category_id

            ORDER BY
                c.complaint_date DESC,
                c.complaint_id DESC
            """
        )


    # ========================================================
    # CATEGORIES
    # ========================================================

    categories = fetch_all(
        """
        SELECT
            category_id,
            category_name,
            description
        FROM complaint_categories
        ORDER BY category_name
        """
    )


    # ========================================================
    # STUDENTS
    # ========================================================

    if role == "Student":

        students_list = []

    else:

        students_list = fetch_all(
            """
            SELECT
                student_id,
                register_number,
                student_name
            FROM students
            ORDER BY register_number
            """
        )


    return render_template(
        "complaints.html",

        complaints=complaints_data,
        categories=categories,
        students=students_list,

        role=role
    )


# ============================================================
# ADD COMPLAINT
# ============================================================

@app.route(
    "/complaints/add",
    methods=["POST"]
)
@login_required
def add_complaint():

    role = session.get(
        "role"
    )


    if role == "Student":

        student_id = session.get(
            "student_id"
        )

    else:

        student_id = request.form.get(
            "student_id"
        )


    category_id = request.form.get(
        "category_id"
    )

    complaint_title = request.form.get(
        "complaint_title",
        ""
    ).strip()

    complaint_description = request.form.get(
        "complaint_description",
        ""
    ).strip()

    priority = request.form.get(
        "priority",
        "Medium"
    )


    if not student_id or not category_id:

        flash(
            "Student and complaint category are required.",
            "error"
        )

        return redirect(
            url_for("complaints")
        )


    if not complaint_title:

        flash(
            "Complaint title is required.",
            "error"
        )

        return redirect(
            url_for("complaints")
        )


    if priority not in (
        "Low",
        "Medium",
        "High"
    ):

        priority = "Medium"


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO complaints
            (
                student_id,
                category_id,
                complaint_title,
                complaint_description,
                priority,
                complaint_date,
                status
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, 'Pending'
            )
            """,
            (
                student_id,
                category_id,
                complaint_title,
                complaint_description or None,
                priority,
                date.today()
            )
        )

        connection.commit()

        flash(
            "Complaint submitted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to submit complaint: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("complaints")
    )


# ============================================================
# UPDATE COMPLAINT
# ============================================================

@app.route(
    "/complaints/update/<int:complaint_id>",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def update_complaint(complaint_id):

    status = request.form.get(
        "status",
        "Pending"
    )

    assigned_to = request.form.get(
        "assigned_to",
        ""
    ).strip()

    resolution = request.form.get(
        "resolution",
        ""
    ).strip()


    allowed_statuses = (
        "Pending",
        "In Progress",
        "Resolved",
        "Rejected"
    )


    if status not in allowed_statuses:

        flash(
            "Invalid complaint status.",
            "error"
        )

        return redirect(
            url_for("complaints")
        )


    if status == "Resolved":

        resolved_date = date.today()

    else:

        resolved_date = None


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE complaints

            SET
                status = %s,
                assigned_to = %s,
                resolution = %s,
                resolved_date = %s

            WHERE complaint_id = %s
            """,
            (
                status,
                assigned_to or None,
                resolution or None,
                resolved_date,
                complaint_id
            )
        )

        connection.commit()

        flash(
            "Complaint updated successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to update complaint: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("complaints")
    )


# ============================================================
# DELETE COMPLAINT
# ============================================================

@app.route(
    "/complaints/delete/<int:complaint_id>",
    methods=["POST"]
)
@role_required("Admin")
def delete_complaint(complaint_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM complaints
            WHERE complaint_id = %s
            """,
            (complaint_id,)
        )

        connection.commit()

        flash(
            "Complaint deleted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to delete complaint: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("complaints")
    )


# ============================================================
# ADMIN USER MANAGEMENT
# ============================================================

@app.route("/admin")
@role_required("Admin")
def admin():

    users = fetch_all(
        """
        SELECT
            u.user_id,
            u.username,
            u.role,
            u.student_id,
            u.faculty_id,

            s.student_name,
            s.register_number,

            f.faculty_name

        FROM users u

        LEFT JOIN students s
            ON u.student_id = s.student_id

        LEFT JOIN faculty f
            ON u.faculty_id = f.faculty_id

        ORDER BY u.user_id
        """
    )


    students_list = fetch_all(
        """
        SELECT
            student_id,
            register_number,
            student_name
        FROM students
        ORDER BY register_number
        """
    )


    faculty_list = fetch_all(
        """
        SELECT
            faculty_id,
            faculty_name
        FROM faculty
        ORDER BY faculty_name
        """
    )


    return render_template(
        "admin.html",

        users=users,
        students=students_list,
        faculty=faculty_list,

        role="Admin"
    )


# ============================================================
# ADD USER
# ============================================================

@app.route(
    "/admin/users/add",
    methods=["POST"]
)
@role_required("Admin")
def add_user():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    role = request.form.get(
        "role",
        ""
    )


    student_id = request.form.get(
        "student_id"
    ) or None

    faculty_id = request.form.get(
        "faculty_id"
    ) or None


    allowed_roles = (
        "Admin",
        "Faculty",
        "Student"
    )


    if role not in allowed_roles:

        flash(
            "Invalid role selected.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    if not username or not password:

        flash(
            "Username and password are required.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    if role == "Student":

        if not student_id:

            flash(
                "Student account must be linked to a student.",
                "error"
            )

            return redirect(
                url_for("admin")
            )

        faculty_id = None


    elif role == "Faculty":

        if not faculty_id:

            flash(
                "Faculty account must be linked to a faculty record.",
                "error"
            )

            return redirect(
                url_for("admin")
            )

        student_id = None


    else:

        student_id = None
        faculty_id = None


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                role,
                student_id,
                faculty_id
            )
            VALUES
            (
                %s, %s, %s, %s, %s
            )
            """,
            (
                username,
                password,
                role,
                student_id,
                faculty_id
            )
        )

        connection.commit()

        flash(
            "User account created successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to create user: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# DELETE USER
# ============================================================

@app.route(
    "/admin/users/delete/<int:user_id>",
    methods=["POST"]
)
@role_required("Admin")
def delete_user(user_id):

    current_user_id = session.get(
        "user_id"
    )


    if user_id == current_user_id:

        flash(
            "You cannot delete your own logged-in account.",
            "error"
        )

        return redirect(
            url_for("admin")
        )


    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        connection.commit()

        flash(
            "User account deleted successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to delete user: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("admin")
    )


# ============================================================
# ADVANCED DBMS FEATURES
# ============================================================

@app.route("/dbms-features")
@login_required
def dbms_features():

    role = session.get(
        "role"
    )


    # ========================================================
    # VIEW 1
    # ========================================================

    academic_summary = fetch_all(
        """
        SELECT *
        FROM student_academic_summary
        LIMIT 100
        """
    )


    # ========================================================
    # VIEW 2
    # ========================================================

    placement_status = fetch_all(
        """
        SELECT *
        FROM student_placement_status
        LIMIT 100
        """
    )


    # ========================================================
    # VIEW 3
    # ========================================================

    booking_details = fetch_all(
        """
        SELECT *
        FROM room_booking_details
        LIMIT 100
        """
    )


    # ========================================================
    # LOW ATTENDANCE STORED PROCEDURE
    # ========================================================

    low_attendance = []

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.callproc(
            "GetLowAttendanceStudents",
            (75.00,)
        )


        for result in cursor.stored_results():

            low_attendance.extend(
                result.fetchall()
            )

    except mysql.connector.Error:

        low_attendance = []

    finally:

        cursor.close()
        connection.close()


    # ========================================================
    # ATTENDANCE WARNINGS
    # ========================================================

    attendance_warnings = fetch_all(
        """
        SELECT
            aw.*,

            s.student_name,
            c.course_code

        FROM attendance_warnings aw

        LEFT JOIN students s
            ON aw.student_id = s.student_id

        LEFT JOIN courses c
            ON aw.course_id = c.course_id

        ORDER BY
            aw.warning_id DESC

        LIMIT 100
        """
    )


    # ========================================================
    # EXPLAIN
    # ========================================================

    explain_result = fetch_all(
        """
        EXPLAIN
        SELECT *
        FROM attendance
        WHERE student_id = 1
        """
    )


    return render_template(
        "dbms_features.html",

        academic_summary=academic_summary,

        placement_status=placement_status,

        booking_details=booking_details,

        low_attendance=low_attendance,

        attendance_warnings=attendance_warnings,

        explain_result=explain_result,

        role=role
    )


# ============================================================
# RUN ATTENDANCE WARNING PROCEDURE
# ============================================================

@app.route(
    "/dbms-features/run-warnings",
    methods=["POST"]
)
@role_required("Admin", "Faculty")
def run_attendance_warnings():

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        cursor.callproc(
            "GenerateAttendanceWarnings"
        )

        connection.commit()

        flash(
            "Attendance warning procedure executed successfully.",
            "success"
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to generate attendance warnings: {error}",
            "error"
        )

    finally:

        cursor.close()
        connection.close()


    return redirect(
        url_for("dbms_features")
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(403)
def forbidden(error):

    return render_template(
        "error.html",
        error_code=403,
        error_message="You do not have permission to access this page."
    ), 403


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "error.html",
        error_code=404,
        error_message="The requested page was not found."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "error.html",
        error_code=500,
        error_message="An unexpected server error occurred."
    ), 500


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )