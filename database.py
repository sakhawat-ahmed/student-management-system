import sqlite3
import bcrypt
import streamlit as st

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('student_management.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        
    def create_tables(self):
        """Create all required tables"""
        try:
            cursor = self.conn.cursor()
            
            # Users table WITHOUT is_active column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    roll_number TEXT UNIQUE NOT NULL,
                    class_name TEXT NOT NULL,
                    section TEXT NOT NULL,
                    dob TEXT,
                    phone TEXT,
                    address TEXT,
                    guardian_name TEXT,
                    guardian_phone TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Teachers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    employee_id TEXT UNIQUE NOT NULL,
                    department TEXT,
                    qualification TEXT,
                    specialization TEXT,
                    experience INTEGER DEFAULT 0,
                    phone TEXT,
                    address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Courses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT UNIQUE NOT NULL,
                    course_name TEXT NOT NULL,
                    description TEXT,
                    credits INTEGER DEFAULT 3,
                    department TEXT,
                    semester INTEGER,
                    max_students INTEGER DEFAULT 50,
                    teacher_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL
                )
            ''')
            
            # Enrollments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS enrollments (
                    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    enrollment_date TEXT DEFAULT CURRENT_DATE,
                    status TEXT DEFAULT 'enrolled',
                    grade TEXT,
                    marks REAL DEFAULT 0,
                    attendance_percentage REAL DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                    UNIQUE(student_id, course_id)
                )
            ''')
            
            # Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT DEFAULT 'absent',
                    remarks TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                    UNIQUE(student_id, course_id, date)
                )
            ''')
            
            # Assignments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignments (
                    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    total_marks REAL NOT NULL,
                    weightage REAL DEFAULT 100,
                    due_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
                )
            ''')
            
            # Grades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grades (
                    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    assignment_id INTEGER NOT NULL,
                    marks_obtained REAL DEFAULT 0,
                    remarks TEXT,
                    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE,
                    UNIQUE(student_id, assignment_id)
                )
            ''')
            
            # Assignment Submissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignment_submissions (
                    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    submission_file TEXT,
                    submission_text TEXT,
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'submitted',
                    marks_obtained REAL,
                    feedback TEXT,
                    graded_by INTEGER,
                    graded_at TIMESTAMP,
                    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                    FOREIGN KEY (graded_by) REFERENCES teachers(teacher_id) ON DELETE SET NULL,
                    UNIQUE(assignment_id, student_id)
                )
            ''')
            
            self.conn.commit()
            
            # Create default admin if not exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
                cursor.execute(
                    "INSERT INTO users (username, password, role, email, full_name) VALUES (?, ?, ?, ?, ?)",
                    ('admin', hashed_password, 'admin', 'admin@sms.com', 'System Administrator')
                )
                self.conn.commit()
                st.success("✅ Default admin user created: username='admin', password='admin123'")
            
            cursor.close()
            return True
            
        except Exception as e:
            st.error(f"❌ Error creating tables: {str(e)}")
            return False
    
    # User Management
    def authenticate_user(self, username, password):
        """Authenticate user login - WITHOUT is_active check"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                user_dict = dict(user)
                if bcrypt.checkpw(password.encode(), user_dict['password'].encode()):
                    return user_dict
            return None
        except Exception as e:
            st.error(f"❌ Authentication error: {str(e)}")
            return None
    
    def create_user(self, username, password, role, email, full_name):
        """Create new user"""
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role, email, full_name) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, role, email, full_name)
            )
            user_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            return user_id
        except Exception as e:
            st.error(f"❌ Error creating user: {str(e)}")
            return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY role, username")
            users = cursor.fetchall()
            cursor.close()
            return [dict(user) for user in users]
        except Exception as e:
            st.error(f"❌ Error fetching users: {str(e)}")
            return []
    
    # Student Management
    def create_student(self, user_id, roll_number, class_name, section, dob, phone, address, guardian_name, guardian_phone):
        """Create student profile"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO students (user_id, roll_number, class_name, section, 
                dob, phone, address, guardian_name, guardian_phone) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, roll_number, class_name, section, dob, phone, 
                 address, guardian_name, guardian_phone)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"❌ Error creating student: {str(e)}")
            return False
    
    def get_all_students(self):
        """Get all students with user details"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username, u.email, u.full_name, u.role
                FROM students s 
                JOIN users u ON s.user_id = u.user_id
                ORDER BY s.class_name, s.section, s.roll_number
            """)
            students = cursor.fetchall()
            cursor.close()
            return [dict(student) for student in students]
        except Exception as e:
            st.error(f"❌ Error fetching students: {str(e)}")
            return []
    
    def get_student_by_user_id(self, user_id):
        """Get student by user ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username, u.email, u.full_name
                FROM students s 
                JOIN users u ON s.user_id = u.user_id
                WHERE s.user_id = ?
            """, (user_id,))
            student = cursor.fetchone()
            cursor.close()
            return dict(student) if student else None
        except Exception as e:
            st.error(f"❌ Error fetching student: {str(e)}")
            return None
    
    def get_student_enrollments(self, student_id):
        """Get all courses a student is enrolled in"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT e.*, c.course_code, c.course_name, c.credits, 
                       u.full_name as teacher_name,
                       t.teacher_id
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                LEFT JOIN users u ON t.user_id = u.user_id
                WHERE e.student_id = ? AND e.status = 'enrolled'
                ORDER BY c.semester, c.course_code
            """, (student_id,))
            enrollments = cursor.fetchall()
            cursor.close()
            return [dict(enrollment) for enrollment in enrollments]
        except Exception as e:
            st.error(f"❌ Error fetching enrollments: {str(e)}")
            return []
    
    # Teacher Management
    def create_teacher(self, user_id, employee_id, department, qualification, specialization, experience, phone, address):
        """Create teacher profile"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO teachers (user_id, employee_id, department, 
                qualification, specialization, experience, phone, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, employee_id, department, qualification, 
                 specialization, experience, phone, address)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"❌ Error creating teacher: {str(e)}")
            return False
    
    def get_all_teachers(self):
        """Get all teachers with user details"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.*, u.username, u.email, u.full_name, u.role
                FROM teachers t 
                JOIN users u ON t.user_id = u.user_id
                ORDER BY t.department, t.employee_id
            """)
            teachers = cursor.fetchall()
            cursor.close()
            return [dict(teacher) for teacher in teachers]
        except Exception as e:
            st.error(f"❌ Error fetching teachers: {str(e)}")
            return []
    
    def get_teacher_by_user_id(self, user_id):
        """Get teacher by user ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.*, u.username, u.email, u.full_name
                FROM teachers t 
                JOIN users u ON t.user_id = u.user_id
                WHERE t.user_id = ?
            """, (user_id,))
            teacher = cursor.fetchone()
            cursor.close()
            return dict(teacher) if teacher else None
        except Exception as e:
            st.error(f"❌ Error fetching teacher: {str(e)}")
            return None
    
    def get_courses_by_teacher(self, teacher_id):
        """Get courses assigned to a teacher"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    c.*,
                    ut.full_name as teacher_name,
                    COUNT(DISTINCT e.student_id) as enrolled_students
                FROM courses c 
                LEFT JOIN enrollments e ON c.course_id = e.course_id AND e.status = 'enrolled'
                LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                LEFT JOIN users ut ON t.user_id = ut.user_id
                WHERE c.teacher_id = ?
                GROUP BY c.course_id
                ORDER BY c.semester, c.course_code
            """, (teacher_id,))
            courses = cursor.fetchall()
            cursor.close()
            return [dict(course) for course in courses]
        except Exception as e:
            st.error(f"❌ Error fetching teacher courses: {str(e)}")
            return []
    
    # Course Management
    def create_course(self, course_code, course_name, description, credits, department, semester, max_students, teacher_id=None):
        """Create new course"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO courses (course_code, course_name, description, 
                credits, department, semester, max_students, teacher_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (course_code, course_name, description, credits, 
                 department, semester, max_students, teacher_id)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"❌ Error creating course: {str(e)}")
            return False
    
    def get_all_courses(self):
        """Get all courses with teacher details"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    c.*, 
                    t.employee_id, 
                    u.full_name as teacher_name, 
                    COUNT(DISTINCT e.student_id) as enrolled_students
                FROM courses c 
                LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                LEFT JOIN users u ON t.user_id = u.user_id
                LEFT JOIN enrollments e ON c.course_id = e.course_id AND e.status = 'enrolled'
                GROUP BY c.course_id
                ORDER BY c.department, c.semester, c.course_code
            """)
            courses = cursor.fetchall()
            cursor.close()
            return [dict(course) for course in courses]
        except Exception as e:
            st.error(f"❌ Error fetching courses: {str(e)}")
            return []
    
    def get_available_courses_for_student(self, student_id):
        """Get courses available for a student to enroll"""
        try:
            cursor = self.conn.cursor()
            # Get all courses not enrolled in
            cursor.execute("""
                SELECT 
                    c.*,
                    u.full_name as teacher_name
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                LEFT JOIN users u ON t.user_id = u.user_id
                WHERE c.course_id NOT IN (
                    SELECT course_id FROM enrollments 
                    WHERE student_id = ? AND status = 'enrolled'
                )
                ORDER BY c.course_code
            """, (student_id,))
            courses = cursor.fetchall()
            cursor.close()
            return [dict(course) for course in courses]
        except Exception as e:
            st.error(f"❌ Error fetching available courses: {str(e)}")
            return []
    
    def enroll_student_in_course(self, student_id, course_id):
        """Enroll student in a course"""
        try:
            cursor = self.conn.cursor()
            
            # Check if course exists and has a teacher assigned
            cursor.execute("SELECT teacher_id FROM courses WHERE course_id = ?", (course_id,))
            course = cursor.fetchone()
            if not course:
                st.error("❌ Course not found")
                return False
            
            # Check if already enrolled
            cursor.execute("""
                SELECT * FROM enrollments 
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id))
            if cursor.fetchone():
                st.warning("⚠️ Student is already enrolled in this course")
                return False
            
            # Enroll the student
            cursor.execute("""
                INSERT INTO enrollments (student_id, course_id, enrollment_date, status) 
                VALUES (?, ?, DATE('now'), 'enrolled')
            """, (student_id, course_id))
            self.conn.commit()
            
            st.success(f"✅ Student successfully enrolled in course!")
            cursor.close()
            return True
        except Exception as e:
            st.error(f"❌ Error enrolling student: {str(e)}")
            return False
    
    def get_course_enrollments(self, course_id):
        """Get all students enrolled in a course"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    e.*, 
                    s.roll_number, 
                    s.class_name, 
                    s.section, 
                    u.full_name as student_name, 
                    e.grade, 
                    e.marks
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE e.course_id = ? AND e.status = 'enrolled'
                ORDER BY s.roll_number
            """, (course_id,))
            enrollments = cursor.fetchall()
            cursor.close()
            return [dict(enrollment) for enrollment in enrollments]
        except Exception as e:
            st.error(f"❌ Error fetching course enrollments: {str(e)}")
            return []
    
    def get_students_by_teacher(self, teacher_id):
        """Get all students taught by a specific teacher"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT DISTINCT
                    s.student_id,
                    s.roll_number,
                    s.class_name,
                    s.section,
                    u.full_name as student_name,
                    u.email as student_email,
                    c.course_code,
                    c.course_name,
                    ut.full_name as teacher_name
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                JOIN courses c ON e.course_id = c.course_id
                LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                LEFT JOIN users ut ON t.user_id = ut.user_id
                WHERE c.teacher_id = ?
                ORDER BY s.roll_number, c.course_code
            """, (teacher_id,))
            students = cursor.fetchall()
            cursor.close()
            return [dict(student) for student in students]
        except Exception as e:
            st.error(f"❌ Error fetching students by teacher: {str(e)}")
            return []
    
    # Attendance
    def mark_attendance(self, student_id, course_id, date, status, remarks=""):
        """Mark attendance for a student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO attendance 
                (student_id, course_id, date, status, remarks)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, course_id, date, status, remarks))
            self.conn.commit()
            
            # Update attendance percentage in enrollments
            cursor.execute("""
                UPDATE enrollments 
                SET attendance_percentage = (
                    SELECT 
                        ROUND((COUNT(CASE WHEN status IN ('present', 'late') THEN 1 END) * 100.0 / COUNT(*)), 2)
                    FROM attendance 
                    WHERE student_id = ? AND course_id = ?
                )
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id, student_id, course_id))
            self.conn.commit()
            
            cursor.close()
            return True
        except Exception as e:
            st.error(f"❌ Error marking attendance: {str(e)}")
            return False
    
    def get_student_attendance(self, student_id, course_id=None):
        """Get attendance records for a student"""
        try:
            cursor = self.conn.cursor()
            if course_id:
                cursor.execute("""
                    SELECT a.*, c.course_code, c.course_name
                    FROM attendance a
                    JOIN courses c ON a.course_id = c.course_id
                    WHERE a.student_id = ? AND a.course_id = ?
                    ORDER BY a.date DESC
                """, (student_id, course_id))
            else:
                cursor.execute("""
                    SELECT a.*, c.course_code, c.course_name
                    FROM attendance a
                    JOIN courses c ON a.course_id = c.course_id
                    WHERE a.student_id = ?
                    ORDER BY a.date DESC
                """, (student_id,))
            
            attendance = cursor.fetchall()
            cursor.close()
            return [dict(record) for record in attendance]
        except Exception as e:
            st.error(f"❌ Error fetching attendance: {str(e)}")
            return []
    
    # Assignments and Grades
    def create_assignment(self, course_id, teacher_id, title, description, total_marks, weightage, due_date):
        """Create new assignment"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO assignments 
                (course_id, teacher_id, title, description, total_marks, weightage, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (course_id, teacher_id, title, description, total_marks, weightage, due_date))
            
            assignment_id = cursor.lastrowid
            
            # Auto-create grade entries for all enrolled students
            cursor.execute("""
                INSERT INTO grades (student_id, assignment_id, marks_obtained, remarks)
                SELECT e.student_id, ?, 0, ''
                FROM enrollments e
                WHERE e.course_id = ? AND e.status = 'enrolled'
            """, (assignment_id, course_id))
            
            self.conn.commit()
            cursor.close()
            return assignment_id
        except Exception as e:
            st.error(f"❌ Error creating assignment: {str(e)}")
            return None
    
    def get_assignments_by_course(self, course_id):
        """Get all assignments for a course"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT a.*, u.full_name as teacher_name
                FROM assignments a
                JOIN teachers t ON a.teacher_id = t.teacher_id
                JOIN users u ON t.user_id = u.user_id
                WHERE a.course_id = ?
                ORDER BY a.due_date
            """, (course_id,))
            assignments = cursor.fetchall()
            cursor.close()
            return [dict(assignment) for assignment in assignments]
        except Exception as e:
            st.error(f"❌ Error fetching assignments: {str(e)}")
            return []
    
    def get_assignment_grades(self, assignment_id):
        """Get all grades for an assignment"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    g.*, 
                    s.roll_number, 
                    u.full_name as student_name,
                    a.total_marks,
                    c.course_code,
                    c.course_name
                FROM grades g
                JOIN students s ON g.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                JOIN assignments a ON g.assignment_id = a.assignment_id
                JOIN courses c ON a.course_id = c.course_id
                WHERE g.assignment_id = ?
                ORDER BY s.roll_number
            """, (assignment_id,))
            grades = cursor.fetchall()
            cursor.close()
            return [dict(grade) for grade in grades]
        except Exception as e:
            st.error(f"❌ Error fetching assignment grades: {str(e)}")
            return []
    
    def update_grade(self, student_id, assignment_id, marks_obtained, remarks=""):
        """Update grade for a student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO grades 
                (student_id, assignment_id, marks_obtained, remarks)
                VALUES (?, ?, ?, ?)
            """, (student_id, assignment_id, marks_obtained, remarks))
            
            # Calculate course marks average
            cursor.execute("""
                SELECT a.course_id
                FROM assignments a
                WHERE a.assignment_id = ?
            """, (assignment_id,))
            course = cursor.fetchone()
            
            if course:
                course_id = course[0]
                cursor.execute("""
                    UPDATE enrollments 
                    SET marks = (
                        SELECT ROUND(AVG(g.marks_obtained * 100.0 / a.total_marks), 2)
                        FROM grades g
                        JOIN assignments a ON g.assignment_id = a.assignment_id
                        WHERE g.student_id = ? AND a.course_id = ?
                    )
                    WHERE student_id = ? AND course_id = ?
                """, (student_id, course_id, student_id, course_id))
            
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"❌ Error updating grade: {str(e)}")
            return False
    
    def get_student_grades(self, student_id, course_id=None):
        """Get grades for a student"""
        try:
            cursor = self.conn.cursor()
            if course_id:
                cursor.execute("""
                    SELECT g.*, a.title, a.total_marks, c.course_code, c.course_name
                    FROM grades g
                    JOIN assignments a ON g.assignment_id = a.assignment_id
                    JOIN courses c ON a.course_id = c.course_id
                    WHERE g.student_id = ? AND a.course_id = ?
                    ORDER BY a.due_date
                """, (student_id, course_id))
            else:
                cursor.execute("""
                    SELECT g.*, a.title, a.total_marks, c.course_code, c.course_name
                    FROM grades g
                    JOIN assignments a ON g.assignment_id = a.assignment_id
                    JOIN courses c ON a.course_id = c.course_id
                    WHERE g.student_id = ?
                    ORDER BY c.course_code, a.due_date
                """, (student_id,))
            
            grades = cursor.fetchall()
            cursor.close()
            return [dict(grade) for grade in grades]
        except Exception as e:
            st.error(f"❌ Error fetching grades: {str(e)}")
            return []