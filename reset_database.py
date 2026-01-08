import os
import sqlite3
import bcrypt

def complete_reset():
    print("🔄 Performing complete system reset...")
    
    # Remove old database file
    if os.path.exists('student_management.db'):
        os.remove('student_management.db')
        print("✅ Old database removed")
    
    # Create new database
    conn = sqlite3.connect('student_management.db')
    cursor = conn.cursor()
    
    # Create all tables
    print("Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
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
        CREATE TABLE students (
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
        CREATE TABLE teachers (
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
        CREATE TABLE courses (
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
        CREATE TABLE enrollments (
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
        CREATE TABLE attendance (
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
        CREATE TABLE assignments (
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
        CREATE TABLE grades (
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
    
    # Create default admin
    print("Creating default admin user...")
    hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "INSERT INTO users (username, password, role, email, full_name) VALUES (?, ?, ?, ?, ?)",
        ('admin', hashed_password, 'admin', 'admin@sms.com', 'System Administrator')
    )
    
    # Create sample courses
    print("Creating sample courses...")
    sample_courses = [
        # Class 10 courses (Semester 1)
        ('MAT101', 'Mathematics 10', 'Basic Mathematics for Class 10', 4, 'Mathematics', 1, 50, None),
        ('SCI101', 'Science 10', 'General Science for Class 10', 4, 'Science', 1, 50, None),
        ('ENG101', 'English 10', 'English Language and Literature', 3, 'English', 1, 50, None),
        ('SOC101', 'Social Studies 10', 'History and Geography', 3, 'Social Studies', 1, 50, None),
        ('CS101', 'Computer Science 10', 'Introduction to Computers', 3, 'Computer Science', 1, 50, None),
        
        # Class 11 courses (Semester 2)
        ('MAT201', 'Mathematics 11', 'Intermediate Mathematics', 4, 'Mathematics', 2, 50, None),
        ('PHY201', 'Physics 11', 'Basic Physics', 4, 'Science', 2, 50, None),
        ('CHE201', 'Chemistry 11', 'Basic Chemistry', 4, 'Science', 2, 50, None),
        ('BIO201', 'Biology 11', 'Basic Biology', 4, 'Science', 2, 50, None),
        ('ENG201', 'English 11', 'Advanced English', 3, 'English', 2, 50, None),
        
        # Class 12 courses (Semester 3)
        ('MAT301', 'Mathematics 12', 'Advanced Mathematics', 4, 'Mathematics', 3, 50, None),
        ('PHY301', 'Physics 12', 'Advanced Physics', 4, 'Science', 3, 50, None),
        ('CHE301', 'Chemistry 12', 'Advanced Chemistry', 4, 'Science', 3, 50, None),
        ('BIO301', 'Biology 12', 'Advanced Biology', 4, 'Science', 3, 50, None),
        ('CS301', 'Computer Science 12', 'Programming Fundamentals', 4, 'Computer Science', 3, 50, None),
    ]
    
    for course in sample_courses:
        cursor.execute("""
            INSERT INTO courses 
            (course_code, course_name, description, credits, department, semester, max_students, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, course)
    
    conn.commit()
    conn.close()
    
    print("\n✅ Complete reset successful!")
    print("\n📋 Default Admin Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n📚 Available Courses by Class:")
    print("   Class 10: Mathematics 10, Science 10, English 10, Social Studies 10, Computer Science 10")
    print("   Class 11: Mathematics 11, Physics 11, Chemistry 11, Biology 11, English 11")
    print("   Class 12: Mathematics 12, Physics 12, Chemistry 12, Biology 12, Computer Science 12")
    print("\n🎉 You can now run the application!")

if __name__ == "__main__":
    complete_reset()