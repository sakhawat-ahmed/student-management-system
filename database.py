import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = self.get_connection()
        
    def get_connection(self):
        """Get SQLite database connection"""
        try:
            conn = sqlite3.connect('student_management.db', check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None
    
    def create_tables(self):
        """Create all required tables"""
        queries = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'teacher', 'student')) NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
            """,
            # Students table
            """
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
                enrollment_date TEXT DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """,
            # Teachers table
            """
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
                hire_date TEXT DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """,
            # Courses table
            """
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
            """,
            # Enrollments table
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TEXT DEFAULT CURRENT_DATE,
                status TEXT CHECK(status IN ('enrolled', 'completed', 'dropped')) DEFAULT 'enrolled',
                grade TEXT,
                marks REAL DEFAULT 0,
                attendance_percentage REAL DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            )
            """,
            # Attendance table
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT CHECK(status IN ('present', 'absent', 'late', 'excused')) DEFAULT 'absent',
                remarks TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id, date)
            )
            """,
            # Assignments/Grades table
            """
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
            """,
            # Grades table
            """
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
            """,
            # Messages/Notifications table
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                subject TEXT,
                content TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        ]
        
        try:
            cursor = self.conn.cursor()
            for query in queries:
                cursor.execute(query)
            self.conn.commit()
            
            # Create default admin if not exists
            self.create_default_admin()
            
            st.success("✅ Database tables created successfully!")
            return True
        except Exception as e:
            st.error(f"Error creating tables: {e}")
            return False
    
    def create_default_admin(self):
        """Create default admin user"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
                cursor.execute(
                    """INSERT INTO users (username, password, role, email, full_name) 
                    VALUES (?, ?, ?, ?, ?)""",
                    ('admin', hashed_password, 'admin', 'admin@sms.com', 'System Administrator')
                )
                self.conn.commit()
                st.info("Default admin created: username='admin', password='admin123'")
            cursor.close()
        except Exception as e:
            st.error(f"Error creating admin: {e}")
    
    # User Management Methods
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                user_dict = dict(user)
                if bcrypt.checkpw(password.encode(), user_dict['password'].encode()):
                    return user_dict
            return None
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
    
    def create_user(self, username, password, role, email, full_name):
        """Create new user"""
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO users (username, password, role, email, full_name) 
                VALUES (?, ?, ?, ?, ?)""",
                (username, hashed_password, role, email, full_name)
            )
            user_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            return user_id
        except Exception as e:
            st.error(f"Error creating user: {e}")
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
            st.error(f"Error fetching users: {e}")
            return []
    
    def update_user(self, user_id, email=None, full_name=None, is_active=None):
        """Update user details"""
        try:
            cursor = self.conn.cursor()
            updates = []
            params = []
            
            if email:
                updates.append("email = ?")
                params.append(email)
            if full_name:
                updates.append("full_name = ?")
                params.append(full_name)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
                cursor.execute(query, params)
                self.conn.commit()
            
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete user (cascade delete from related tables)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False
    
    # Student Management Methods
    def create_student(self, user_id, roll_number, class_name, section, dob, 
                      phone, address, guardian_name, guardian_phone):
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
            st.error(f"Error creating student: {e}")
            return False
    
    def get_all_students(self):
        """Get all students with user details"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username, u.email, u.full_name, u.role, u.is_active
                FROM students s 
                JOIN users u ON s.user_id = u.user_id
                ORDER BY s.class_name, s.section, s.roll_number
            """)
            students = cursor.fetchall()
            cursor.close()
            return [dict(student) for student in students]
        except Exception as e:
            st.error(f"Error fetching students: {e}")
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
            st.error(f"Error fetching student: {e}")
            return None
    
    # Teacher Management Methods
    def create_teacher(self, user_id, employee_id, department, qualification, 
                      specialization, experience, phone, address):
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
            st.error(f"Error creating teacher: {e}")
            return False
    
    def get_all_teachers(self):
        """Get all teachers with user details"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT t.*, u.username, u.email, u.full_name, u.role, u.is_active
                FROM teachers t 
                JOIN users u ON t.user_id = u.user_id
                ORDER BY t.department, t.employee_id
            """)
            teachers = cursor.fetchall()
            cursor.close()
            return [dict(teacher) for teacher in teachers]
        except Exception as e:
            st.error(f"Error fetching teachers: {e}")
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
            st.error(f"Error fetching teacher: {e}")
            return None
    
    # Course Management Methods
    def create_course(self, course_code, course_name, description, credits, 
                     department, semester, max_students, teacher_id=None):
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
            st.error(f"Error creating course: {e}")
            return False
    
    def get_all_courses(self):
        """Get all courses with teacher details"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.*, t.employee_id, u.full_name as teacher_name, 
                       COUNT(e.student_id) as enrolled_students
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
            st.error(f"Error fetching courses: {e}")
            return []
    
    def get_courses_by_teacher(self, teacher_id):
        """Get courses assigned to a teacher"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT c.*, COUNT(e.student_id) as enrolled_students
                FROM courses c 
                LEFT JOIN enrollments e ON c.course_id = e.course_id AND e.status = 'enrolled'
                WHERE c.teacher_id = ?
                GROUP BY c.course_id
                ORDER BY c.semester, c.course_code
            """, (teacher_id,))
            courses = cursor.fetchall()
            cursor.close()
            return [dict(course) for course in courses]
        except Exception as e:
            st.error(f"Error fetching teacher courses: {e}")
            return []
    
    def get_available_courses_for_student(self, student_id):
        """Get courses available for a student to enroll"""
        try:
            cursor = self.conn.cursor()
            # Get student's class and semester
            cursor.execute("""
                SELECT class_name FROM students WHERE student_id = ?
            """, (student_id,))
            student = cursor.fetchone()
            
            if student:
                class_name = dict(student)['class_name']
                # For simplicity, let's say class 10 = semester 1, 11 = 2, 12 = 3
                semester_map = {'10': 1, '11': 2, '12': 3}
                semester = semester_map.get(class_name, 1)
                
                # Get courses for that semester that student is not enrolled in
                cursor.execute("""
                    SELECT c.*, u.full_name as teacher_name
                    FROM courses c
                    LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                    LEFT JOIN users u ON t.user_id = u.user_id
                    WHERE c.semester = ? 
                    AND c.course_id NOT IN (
                        SELECT course_id FROM enrollments 
                        WHERE student_id = ? AND status = 'enrolled'
                    )
                    ORDER BY c.course_code
                """, (semester, student_id))
                courses = cursor.fetchall()
                cursor.close()
                return [dict(course) for course in courses]
            return []
        except Exception as e:
            st.error(f"Error fetching available courses: {e}")
            return []
    
    # Enrollment Methods
    def enroll_student_in_course(self, student_id, course_id):
        """Enroll student in a course"""
        try:
            cursor = self.conn.cursor()
            # Check if already enrolled
            cursor.execute("""
                SELECT * FROM enrollments 
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id))
            
            if cursor.fetchone():
                st.warning("Student is already enrolled in this course")
                return False
            
            # Enroll student
            cursor.execute("""
                INSERT INTO enrollments (student_id, course_id) 
                VALUES (?, ?)
            """, (student_id, course_id))
            
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error enrolling student: {e}")
            return False
    
    def get_student_enrollments(self, student_id):
        """Get all courses a student is enrolled in"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT e.*, c.course_code, c.course_name, c.credits, 
                       u.full_name as teacher_name, e.grade, e.marks, e.attendance_percentage
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
            st.error(f"Error fetching enrollments: {e}")
            return []
    
    def get_course_enrollments(self, course_id):
        """Get all students enrolled in a course"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT e.*, s.roll_number, s.class_name, s.section, 
                       u.full_name as student_name, e.grade, e.marks
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
            st.error(f"Error fetching course enrollments: {e}")
            return []
    
    # Attendance Methods
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
            self._update_attendance_percentage(student_id, course_id)
            
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error marking attendance: {e}")
            return False
    
    def _update_attendance_percentage(self, student_id, course_id):
        """Update attendance percentage for a student in a course"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total_classes,
                       SUM(CASE WHEN status IN ('present', 'late') THEN 1 ELSE 0 END) as attended_classes
                FROM attendance 
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id))
            
            result = cursor.fetchone()
            if result:
                total = result['total_classes']
                attended = result['attended_classes']
                percentage = (attended / total * 100) if total > 0 else 0
                
                cursor.execute("""
                    UPDATE enrollments 
                    SET attendance_percentage = ?
                    WHERE student_id = ? AND course_id = ?
                """, (percentage, student_id, course_id))
                
                self.conn.commit()
            
            cursor.close()
        except Exception as e:
            st.error(f"Error updating attendance percentage: {e}")
    
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
            st.error(f"Error fetching attendance: {e}")
            return []
    
    # Assignment and Grade Methods
    def create_assignment(self, course_id, teacher_id, title, description, 
                         total_marks, weightage, due_date):
        """Create new assignment"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO assignments 
                (course_id, teacher_id, title, description, total_marks, weightage, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (course_id, teacher_id, title, description, 
                  total_marks, weightage, due_date))
            
            assignment_id = cursor.lastrowid
            self.conn.commit()
            
            # Create grade entries for all enrolled students
            cursor.execute("""
                INSERT INTO grades (student_id, assignment_id)
                SELECT student_id, ? 
                FROM enrollments 
                WHERE course_id = ? AND status = 'enrolled'
            """, (assignment_id, course_id))
            
            self.conn.commit()
            cursor.close()
            return assignment_id
        except Exception as e:
            st.error(f"Error creating assignment: {e}")
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
            st.error(f"Error fetching assignments: {e}")
            return []
    
    def update_grade(self, student_id, assignment_id, marks_obtained, remarks=""):
        """Update grade for a student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE grades 
                SET marks_obtained = ?, remarks = ?, graded_at = CURRENT_TIMESTAMP
                WHERE student_id = ? AND assignment_id = ?
            """, (marks_obtained, remarks, student_id, assignment_id))
            
            self.conn.commit()
            
            # Update total marks in enrollments
            self._update_course_grade(student_id, assignment_id)
            
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Error updating grade: {e}")
            return False
    
    def _update_course_grade(self, student_id, assignment_id):
        """Update course total marks based on assignment grades"""
        try:
            cursor = self.conn.cursor()
            
            # Get course_id from assignment
            cursor.execute("""
                SELECT course_id FROM assignments WHERE assignment_id = ?
            """, (assignment_id,))
            assignment = cursor.fetchone()
            
            if assignment:
                course_id = assignment['course_id']
                
                # Calculate weighted average
                cursor.execute("""
                    SELECT 
                        SUM(a.weightage) as total_weightage,
                        SUM(g.marks_obtained * a.weightage / a.total_marks) as weighted_score
                    FROM assignments a
                    JOIN grades g ON a.assignment_id = g.assignment_id
                    WHERE a.course_id = ? AND g.student_id = ? 
                    AND g.marks_obtained IS NOT NULL
                """, (course_id, student_id))
                
                result = cursor.fetchone()
                if result and result['total_weightage'] > 0:
                    weighted_score = result['weighted_score']
                    total_weightage = result['total_weightage']
                    final_percentage = (weighted_score / total_weightage) * 100
                    
                    # Convert to grade
                    grade = self._calculate_grade(final_percentage)
                    
                    # Update enrollment record
                    cursor.execute("""
                        UPDATE enrollments 
                        SET marks = ?, grade = ?
                        WHERE student_id = ? AND course_id = ?
                    """, (final_percentage, grade, student_id, course_id))
                    
                    self.conn.commit()
            
            cursor.close()
        except Exception as e:
            st.error(f"Error updating course grade: {e}")
    
    def _calculate_grade(self, percentage):
        """Calculate grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'
    
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
            st.error(f"Error fetching grades: {e}")
            return []
    
    def get_assignment_grades(self, assignment_id):
        """Get all grades for an assignment"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT g.*, s.roll_number, u.full_name as student_name
                FROM grades g
                JOIN students s ON g.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE g.assignment_id = ?
                ORDER BY s.roll_number
            """, (assignment_id,))
            grades = cursor.fetchall()
            cursor.close()
            return [dict(grade) for grade in grades]
        except Exception as e:
            st.error(f"Error fetching assignment grades: {e}")
            return []