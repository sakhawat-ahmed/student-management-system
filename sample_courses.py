import sqlite3
import sys

def create_sample_courses():
    conn = sqlite3.connect('student_management.db')
    cursor = conn.cursor()
    
    # Sample courses for different classes
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
    
    created_count = 0
    for course in sample_courses:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO courses 
                (course_code, course_name, description, credits, department, semester, max_students, teacher_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, course)
            created_count += 1
        except:
            pass
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Created {created_count} sample courses")
    print("\n📚 Available courses by class:")
    print("  Class 10 (Semester 1): Mathematics, Science, English, Social Studies, Computer Science")
    print("  Class 11 (Semester 2): Mathematics, Physics, Chemistry, Biology, English")
    print("  Class 12 (Semester 3): Mathematics, Physics, Chemistry, Biology, Computer Science")

if __name__ == "__main__":
    create_sample_courses()