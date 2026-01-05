import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import Database
import hashlib
import time
import sys

# Page configuration
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

# Initialize database
@st.cache_resource
# Replace the database initialization section with this:

# Initialize database
def init_database():
    try:
        db = Database()
        return db
    except Exception as e:
        st.error(f"❌ Failed to initialize database: {str(e)}")
        return None

db = init_database()
if db is None:
    st.error("Failed to connect to database. Please check the console for errors.")
    st.stop()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'page' not in st.session_state:
    st.session_state.page = "login"

# Helper function for rerun
def rerun_app():
    """Rerun the app - compatible with older Streamlit versions"""
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    elif hasattr(st, 'rerun'):
        st.rerun()
    else:
        # Manual rerun by raising an exception
        raise st.script_runner.RerunException(st.script_runner.RerunData(None))

# Authentication functions
def login():
    st.title("🎓 Student Management System")
    st.markdown("---")
    
    # Create a centered login form using HTML/CSS
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f9f9f9;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-title {
        text-align: center;
        color: #333;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="login-title">🔐 Login</h3>', unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    # Create two columns for buttons without nesting
    col1, col2 = st.columns(2)
    
    with col1:
        login_clicked = st.button("Login")
        
    with col2:
        register_clicked = st.button("Register")
    
    if login_clicked:
        if username and password:
            user = db.authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.role = user['role']
                st.session_state.user_id = user['user_id']
                st.session_state.page = "dashboard"
                st.success("Login successful!")
                time.sleep(1)
                rerun_app()
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password")
    
    if register_clicked:
        st.session_state.page = "register"
        rerun_app()
    
    st.markdown('</div>', unsafe_allow_html=True)

def register():
    st.title("📝 User Registration")
    st.markdown("---")
    
    st.markdown("""
    <style>
    .register-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 30px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            username = st.text_input("Username", placeholder="johndoe")
        
        with col2:
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            role = st.selectbox("Role", ["student", "teacher"])
        
        # Additional fields based on role
        if role == "student":
            roll_number = st.text_input("Roll Number", placeholder="S001")
            class_name = st.selectbox("Class", ["10", "11", "12"])
            section = st.selectbox("Section", ["A", "B", "C", "D"])
        else:
            employee_id = st.text_input("Employee ID", placeholder="T001")
            department = st.selectbox("Department", [
                "Mathematics", "Science", "English", 
                "Social Studies", "Computer Science", "Physical Education"
            ])
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not all([full_name, email, username, password, confirm_password]):
                st.error("Please fill all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    # Create user
                    user_id = db.create_user(username, password, role, email, full_name)
                    
                    if user_id:
                        # Create role-specific profile
                        if role == "student":
                            db.create_student(
                                user_id, roll_number, class_name, section,
                                "2000-01-01", "", "", "", ""
                            )
                        else:
                            db.create_teacher(
                                user_id, employee_id, department,
                                "Bachelor's Degree", "General", 0, "", ""
                            )
                        
                        st.success("Registration successful! Please login.")
                        st.session_state.page = "login"
                        time.sleep(2)
                        rerun_app()
                    else:
                        st.error("Registration failed. Username or email might already exist.")
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("← Back to Login"):
        st.session_state.page = "login"
        rerun_app()

# Dashboard functions - ADMIN
def admin_dashboard():
    st.sidebar.title("👨‍💼 Admin Panel")
    
    menu = st.sidebar.selectbox("Navigation", [
        "📊 Dashboard",
        "👥 User Management",
        "🎓 Student Management",
        "👨‍🏫 Teacher Management",
        "📚 Course Management",
        "➕ Create New User",
        "⚙️ System Settings"
    ])
    
    st.title(f"Admin Dashboard - {menu}")
    st.markdown("---")
    
    if menu == "📊 Dashboard":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            students = db.get_all_students()
            st.metric("Total Students", len(students))
        
        with col2:
            teachers = db.get_all_teachers()
            st.metric("Total Teachers", len(teachers))
        
        with col3:
            courses = db.get_all_courses()
            st.metric("Total Courses", len(courses))
        
        with col4:
            users = db.get_all_users()
            st.metric("Total Users", len(users))
        
        # Recent activities
        st.subheader("📈 Recent Activities")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Recent Students**")
            if students:
                df_students = pd.DataFrame(students[:5])
                st.dataframe(df_students[['roll_number', 'full_name', 'class_name', 'section']])
        
        with col2:
            st.write("**Recent Teachers**")
            if teachers:
                df_teachers = pd.DataFrame(teachers[:5])
                st.dataframe(df_teachers[['employee_id', 'full_name', 'department']])
    
    elif menu == "👥 User Management":
        st.subheader("Manage Users")
        
        users = db.get_all_users()
        if users:
            df = pd.DataFrame(users)
            df = df[['user_id', 'username', 'email', 'full_name', 'role', 'is_active', 'created_at']]
            
            # Search and filter
            col1, col2 = st.columns(2)
            with col1:
                search = st.text_input("Search users")
            with col2:
                filter_role = st.selectbox("Filter by role", ["All", "admin", "teacher", "student"])
            
            if search:
                df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
            if filter_role != "All":
                df = df[df['role'] == filter_role]
            
            st.dataframe(df)
            
            # User actions
            st.subheader("User Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("### Update Status")
                user_id = st.number_input("User ID to update", min_value=1, step=1)
                if user_id:
                    is_active = st.selectbox("Status", [1, 0], format_func=lambda x: "Active" if x else "Inactive")
                    if st.button("Update Status"):
                        if db.update_user(user_id, is_active=is_active):
                            st.success("User status updated!")
                            time.sleep(1)
                            rerun_app()
            
            with col2:
                st.write("### Send Message")
                st.info("Message feature will be implemented")
            
            with col3:
                st.write("### Delete User")
                del_user_id = st.number_input("User ID to delete", min_value=1, step=1, key="del_user")
                if st.button("Delete User"):
                    if db.delete_user(del_user_id):
                        st.success("User deleted!")
                        time.sleep(1)
                        rerun_app()
        else:
            st.info("No users found")
    
    elif menu == "🎓 Student Management":
        st.subheader("Student Management")
        
        students = db.get_all_students()
        if students:
            df = pd.DataFrame(students)
            df = df[['student_id', 'roll_number', 'full_name', 'class_name', 
                    'section', 'phone', 'email', 'is_active']]
            
            st.dataframe(df)
            
            # Student details
            st.subheader("Student Details")
            student_options = [f"{s['roll_number']} - {s['full_name']}" for s in students]
            if student_options:
                selected_student = st.selectbox(
                    "Select Student",
                    options=student_options
                )
                
                if selected_student:
                    student_id = int(selected_student.split(" - ")[0][1:])  # Extract ID
                    student = next((s for s in students if s['student_id'] == student_id), None)
                    
                    if student:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {student['full_name']}")
                            st.write(f"**Roll Number:** {student['roll_number']}")
                            st.write(f"**Class:** {student['class_name']} - {student['section']}")
                            st.write(f"**Email:** {student['email']}")
                        
                        with col2:
                            st.write(f"**Phone:** {student['phone'] or 'N/A'}")
                            st.write(f"**Address:** {student['address'] or 'N/A'}")
                            st.write(f"**Guardian:** {student['guardian_name'] or 'N/A'}")
                            st.write(f"**Status:** {'Active' if student['is_active'] else 'Inactive'}")
                        
                        # Student enrollments
                        enrollments = db.get_student_enrollments(student_id)
                        if enrollments:
                            st.subheader("📚 Enrolled Courses")
                            df_enrollments = pd.DataFrame(enrollments)
                            st.dataframe(df_enrollments[['course_code', 'course_name', 'credits', 'grade', 'marks', 'attendance_percentage']])
        else:
            st.info("No students found")
    
    elif menu == "👨‍🏫 Teacher Management":
        st.subheader("Teacher Management")
        
        teachers = db.get_all_teachers()
        if teachers:
            df = pd.DataFrame(teachers)
            df = df[['teacher_id', 'employee_id', 'full_name', 'department', 
                    'qualification', 'experience', 'phone', 'email', 'is_active']]
            
            st.dataframe(df)
            
            # Teacher details and courses
            teacher_options = [f"{t['employee_id']} - {t['full_name']}" for t in teachers]
            if teacher_options:
                selected_teacher = st.selectbox(
                    "Select Teacher",
                    options=teacher_options
                )
                
                if selected_teacher:
                    teacher_id = int(selected_teacher.split(" - ")[0][1:])
                    teacher = next((t for t in teachers if t['teacher_id'] == teacher_id), None)
                    
                    if teacher:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Name:** {teacher['full_name']}")
                            st.write(f"**Employee ID:** {teacher['employee_id']}")
                            st.write(f"**Department:** {teacher['department']}")
                            st.write(f"**Email:** {teacher['email']}")
                        
                        with col2:
                            st.write(f"**Qualification:** {teacher['qualification']}")
                            st.write(f"**Experience:** {teacher['experience']} years")
                            st.write(f"**Phone:** {teacher['phone'] or 'N/A'}")
                            st.write(f"**Status:** {'Active' if teacher['is_active'] else 'Inactive'}")
                        
                        # Teacher's courses
                        courses = db.get_courses_by_teacher(teacher_id)
                        if courses:
                            st.subheader("📚 Assigned Courses")
                            df_courses = pd.DataFrame(courses)
                            st.dataframe(df_courses[['course_code', 'course_name', 'credits', 'semester', 'enrolled_students']])
        else:
            st.info("No teachers found")
    
    elif menu == "📚 Course Management":
        st.subheader("Course Management")
        
        courses = db.get_all_courses()
        if courses:
            df = pd.DataFrame(courses)
            df = df[['course_id', 'course_code', 'course_name', 'credits', 
                    'department', 'semester', 'teacher_name', 'enrolled_students']]
            
            st.dataframe(df)
            
            # Course creation
            st.subheader("➕ Create New Course")
            with st.form("create_course_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    course_code = st.text_input("Course Code", placeholder="CS101")
                    course_name = st.text_input("Course Name", placeholder="Introduction to Programming")
                    credits = st.number_input("Credits", min_value=1, max_value=5, value=3)
                
                with col2:
                    department = st.selectbox("Department", [
                        "Computer Science", "Mathematics", "Science", 
                        "English", "Social Studies", "Physical Education"
                    ])
                    semester = st.number_input("Semester", min_value=1, max_value=8, value=1)
                    max_students = st.number_input("Max Students", min_value=10, max_value=100, value=50)
                
                description = st.text_area("Course Description")
                
                # Teacher assignment
                teachers = db.get_all_teachers()
                teacher_options = ["Not Assigned"] + [f"{t['employee_id']} - {t['full_name']}" for t in teachers]
                selected_teacher = st.selectbox("Assign Teacher", options=teacher_options)
                
                submitted = st.form_submit_button("Create Course")
                
                if submitted:
                    teacher_id = None
                    if selected_teacher and selected_teacher != "Not Assigned":
                        teacher_id = int(selected_teacher.split(" - ")[0][1:])
                    
                    if db.create_course(course_code, course_name, description, credits, 
                                      department, semester, max_students, teacher_id):
                        st.success("Course created successfully!")
                        time.sleep(1)
                        rerun_app()
        else:
            st.info("No courses found")
    
    elif menu == "➕ Create New User":
        st.subheader("Create New User")
        
        with st.form("create_user_form"):
            role = st.selectbox("Role", ["student", "teacher", "admin"])
            
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                username = st.text_input("Username")
            
            with col2:
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            # Role-specific fields
            if role == "student":
                roll_number = st.text_input("Roll Number")
                class_name = st.selectbox("Class", ["10", "11", "12"])
                section = st.selectbox("Section", ["A", "B", "C", "D"])
            elif role == "teacher":
                employee_id = st.text_input("Employee ID")
                department = st.selectbox("Department", [
                    "Mathematics", "Science", "English", 
                    "Social Studies", "Computer Science", "Physical Education"
                ])
            
            submitted = st.form_submit_button("Create User")
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    user_id = db.create_user(username, password, role, email, full_name)
                    if user_id:
                        if role == "student":
                            db.create_student(user_id, roll_number, class_name, section, 
                                           "2000-01-01", "", "", "", "")
                        elif role == "teacher":
                            db.create_teacher(user_id, employee_id, department, 
                                           "Bachelor's Degree", "General", 0, "", "")
                        
                        st.success(f"{role.capitalize()} user created successfully!")
                        time.sleep(1)
                        rerun_app()
    
    elif menu == "⚙️ System Settings":
        st.subheader("System Settings")
        
        st.write("### Database Information")
        st.info("SQLite database: student_management.db")
        
        if st.button("Reset Database"):
            if db.create_tables():
                st.success("Database reset successfully!")
                time.sleep(1)
                rerun_app()
        
        st.write("### Export Data")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Export Students"):
                students = db.get_all_students()
                if students:
                    df = pd.DataFrame(students)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="students.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("Export Teachers"):
                teachers = db.get_all_teachers()
                if teachers:
                    df = pd.DataFrame(teachers)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="teachers.csv",
                        mime="text/csv"
                    )
        
        with col3:
            if st.button("Export Courses"):
                courses = db.get_all_courses()
                if courses:
                    df = pd.DataFrame(courses)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="courses.csv",
                        mime="text/csv"
                    )

# Dashboard functions - TEACHER
def teacher_dashboard():
    st.sidebar.title("👨‍🏫 Teacher Panel")
    
    # Get teacher details
    teacher = db.get_teacher_by_user_id(st.session_state.user_id)
    
    if teacher:
        st.sidebar.write(f"**Name:** {teacher['full_name']}")
        st.sidebar.write(f"**Employee ID:** {teacher['employee_id']}")
        st.sidebar.write(f"**Department:** {teacher['department']}")
    
    menu_options = [
        "📊 Dashboard",
        "📚 My Courses",
        "👥 My Students",
        "📋 Attendance",
        "📝 Assignments",
        "📊 Grades"
    ]
    menu = st.sidebar.selectbox("Navigation", menu_options)
    
    st.title(f"Teacher Dashboard")
    st.markdown("---")
    
    if not teacher:
        st.error("Teacher profile not found!")
        return
    
    if menu == "📊 Dashboard":
        st.subheader(f"Welcome, {teacher['full_name']}!")
        
        # Get teacher's courses
        courses = db.get_courses_by_teacher(teacher['teacher_id'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Courses", len(courses))
        
        with col2:
            total_students = sum(course.get('enrolled_students', 0) for course in courses)
            st.metric("Total Students", total_students)
        
        with col3:
            st.metric("Department", teacher['department'])
        
        with col4:
            st.metric("Experience", f"{teacher['experience']} years")
        
        # Recent courses
        st.subheader("📚 My Courses")
        if courses:
            df_courses = pd.DataFrame(courses)
            st.dataframe(df_courses[['course_code', 'course_name', 'credits', 'semester', 'enrolled_students']])
        else:
            st.info("No courses assigned yet")
    
    elif menu == "📚 My Courses":
        st.subheader("My Courses")
        
        courses = db.get_courses_by_teacher(teacher['teacher_id'])
        if courses:
            for idx, course in enumerate(courses):
                st.write(f"**{course['course_code']} - {course['course_name']}** ({course['enrolled_students']} students)")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Credits: {course['credits']}")
                    st.write(f"Semester: {course['semester']}")
                    st.write(f"Department: {course['department']}")
                
                with col2:
                    st.write(f"Description: {course['description']}")
                
                # Course actions
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("View Students", key=f"view_{idx}"):
                        # Simplified - just show students
                        enrollments = db.get_course_enrollments(course['course_id'])
                        if enrollments:
                            st.subheader(f"Students in {course['course_code']}")
                            df_students = pd.DataFrame(enrollments)
                            st.dataframe(df_students[['roll_number', 'student_name', 'grade', 'marks']])
                        else:
                            st.info("No students enrolled")
                
                with col_btn2:
                    if st.button("Take Attendance", key=f"att_{idx}"):
                        # Show attendance form directly
                        st.subheader(f"Take Attendance for {course['course_code']}")
                        enrollments = db.get_course_enrollments(course['course_id'])
                        if enrollments:
                            attendance_date = st.date_input("Date", value=date.today(), key=f"date_{idx}")
                            attendance_data = []
                            for stud_idx, enrollment in enumerate(enrollments):
                                st.write(f"{enrollment['roll_number']} - {enrollment['student_name']}")
                                status = st.selectbox(
                                    "Status",
                                    ["present", "absent", "late", "excused"],
                                    key=f"att_status_{idx}_{stud_idx}",
                                    index=1
                                )
                                attendance_data.append({
                                    'student_id': enrollment['student_id'],
                                    'status': status
                                })
                            
                            if st.button("Submit Attendance", key=f"submit_att_{idx}"):
                                success_count = 0
                                for data in attendance_data:
                                    if db.mark_attendance(
                                        data['student_id'], course['course_id'], 
                                        str(attendance_date), data['status']
                                    ):
                                        success_count += 1
                                
                                if success_count == len(attendance_data):
                                    st.success("Attendance marked successfully!")
                                else:
                                    st.warning(f"Marked attendance for {success_count}/{len(attendance_data)} students")
                                time.sleep(1)
                                rerun_app()
                        else:
                            st.info("No students enrolled in this course")
                
                with col_btn3:
                    if st.button("Create Assignment", key=f"assign_{idx}"):
                        # Show assignment form directly
                        st.subheader(f"Create Assignment for {course['course_code']}")
                        with st.form(f"assignment_form_{idx}"):
                            title = st.text_input("Assignment Title", key=f"title_{idx}")
                            description = st.text_area("Description", key=f"desc_{idx}")
                            total_marks = st.number_input("Total Marks", min_value=1, max_value=100, value=100, key=f"marks_{idx}")
                            weightage = st.number_input("Weightage (%)", min_value=1, max_value=100, value=100, key=f"weight_{idx}")
                            due_date = st.date_input("Due Date", value=date.today(), key=f"due_{idx}")
                            
                            if st.form_submit_button("Create Assignment"):
                                assignment_id = db.create_assignment(
                                    course['course_id'], teacher['teacher_id'], title, description,
                                    total_marks, weightage, str(due_date)
                                )
                                if assignment_id:
                                    st.success("Assignment created successfully!")
                                    time.sleep(1)
                                    rerun_app()
                
                st.markdown("---")
        else:
            st.info("No courses assigned")
    
    elif menu == "👥 My Students":
        st.subheader("My Students")
        
        courses = db.get_courses_by_teacher(teacher['teacher_id'])
        if courses:
            all_students = []
            for course in courses:
                enrollments = db.get_course_enrollments(course['course_id'])
                for enrollment in enrollments:
                    enrollment['course_code'] = course['course_code']
                    enrollment['course_name'] = course['course_name']
                    all_students.append(enrollment)
            
            if all_students:
                df = pd.DataFrame(all_students)
                df = df[['roll_number', 'student_name', 'course_code', 'course_name', 'grade', 'marks']]
                st.dataframe(df)
            else:
                st.info("No students enrolled in your courses")
        else:
            st.info("No courses assigned")
    
    elif menu == "📋 Attendance":
        st.subheader("Take Attendance")
        
        courses = db.get_courses_by_teacher(teacher['teacher_id'])
        if courses:
            course_options = [f"{c['course_code']} - {c['course_name']}" for c in courses]
            selected_course = st.selectbox(
                "Select Course",
                options=course_options
            )
            
            if selected_course:
                course_id = next(c['course_id'] for c in courses if f"{c['course_code']} - {c['course_name']}" == selected_course)
                enrollments = db.get_course_enrollments(course_id)
                
                if enrollments:
                    attendance_date = st.date_input("Date", value=date.today())
                    
                    st.write("### Mark Attendance")
                    attendance_data = []
                    for idx, enrollment in enumerate(enrollments):
                        st.write(f"{enrollment['roll_number']} - {enrollment['student_name']}")
                        status = st.selectbox(
                            "Status",
                            ["present", "absent", "late", "excused"],
                            key=f"att_{idx}",
                            index=1
                        )
                        attendance_data.append({
                            'student_id': enrollment['student_id'],
                            'status': status
                        })
                    
                    if st.button("Submit Attendance"):
                        success_count = 0
                        for data in attendance_data:
                            if db.mark_attendance(
                                data['student_id'], course_id, 
                                str(attendance_date), data['status']
                            ):
                                success_count += 1
                        
                        if success_count == len(attendance_data):
                            st.success("Attendance marked successfully!")
                        else:
                            st.warning(f"Marked attendance for {success_count}/{len(attendance_data)} students")
                        time.sleep(1)
                        rerun_app()
                else:
                    st.info("No students enrolled in this course")
        else:
            st.info("No courses assigned")
    
    elif menu == "📝 Assignments":
        st.subheader("Assignments")
        
        courses = db.get_courses_by_teacher(teacher['teacher_id'])
        if courses:
            course_options = [f"{c['course_code']} - {c['course_name']}" for c in courses]
            selected_course = st.selectbox(
                "Select Course",
                options=course_options
            )
            
            if selected_course:
                course_id = next(c['course_id'] for c in courses if f"{c['course_code']} - {c['course_name']}" == selected_course)
                
                # Create new assignment
                st.subheader("Create New Assignment")
                with st.form("create_assignment_form"):
                    title = st.text_input("Assignment Title")
                    description = st.text_area("Description")
                    total_marks = st.number_input("Total Marks", min_value=1, max_value=100, value=100)
                    weightage = st.number_input("Weightage (%)", min_value=1, max_value=100, value=100)
                    due_date = st.date_input("Due Date", value=date.today())
                    
                    submitted = st.form_submit_button("Create Assignment")
                    
                    if submitted:
                        assignment_id = db.create_assignment(
                            course_id, teacher['teacher_id'], title, description,
                            total_marks, weightage, str(due_date)
                        )
                        if assignment_id:
                            st.success("Assignment created successfully!")
                            time.sleep(1)
                            rerun_app()
                
                # View existing assignments
                st.subheader("Existing Assignments")
                assignments = db.get_assignments_by_course(course_id)
                if assignments:
                    for idx, assignment in enumerate(assignments):
                        st.write(f"**{assignment['title']}** - Due: {assignment['due_date']}")
                        st.write(f"Description: {assignment['description']}")
                        st.write(f"Total Marks: {assignment['total_marks']}, Weightage: {assignment['weightage']}%")
                        
                        # Grade assignment
                        if st.button("Grade Assignment", key=f"grade_{idx}"):
                            grades = db.get_assignment_grades(assignment['assignment_id'])
                            if grades:
                                for grade_idx, grade in enumerate(grades):
                                    st.write(f"{grade['roll_number']} - {grade['student_name']}")
                                    current_marks = grade.get('marks_obtained', 0)
                                    marks = st.number_input(
                                        "Marks Obtained", 
                                        min_value=0.0, 
                                        max_value=float(assignment['total_marks']),
                                        value=float(current_marks),
                                        key=f"marks_{idx}_{grade_idx}"
                                    )
                                    remarks = st.text_input("Remarks", value=grade.get('remarks', ''), key=f"remarks_{idx}_{grade_idx}")
                                    
                                    if st.button("Update Grade", key=f"update_{idx}_{grade_idx}"):
                                        if db.update_grade(grade['student_id'], assignment['assignment_id'], marks, remarks):
                                            st.success("Grade updated!")
                                            time.sleep(1)
                                            rerun_app()
                            else:
                                st.info("No students to grade")
                        st.markdown("---")
        else:
            st.info("No courses assigned")
    
    elif menu == "📊 Grades":
        st.subheader("Manage Grades")
        
        courses = db.get_courses_by_teacher(teacher['teacher_id'])
        if courses:
            course_options = [f"{c['course_code']} - {c['course_name']}" for c in courses]
            selected_course = st.selectbox(
                "Select Course",
                options=course_options
            )
            
            if selected_course:
                course_id = next(c['course_id'] for c in courses if f"{c['course_code']} - {c['course_name']}" == selected_course)
                enrollments = db.get_course_enrollments(course_id)
                
                if enrollments:
                    st.write("### Student Grades")
                    for idx, enrollment in enumerate(enrollments):
                        st.write(f"**{enrollment['roll_number']} - {enrollment['student_name']}**")
                        grades = db.get_student_grades(enrollment['student_id'], course_id)
                        if grades:
                            df_grades = pd.DataFrame(grades)
                            df_grades = df_grades[['title', 'marks_obtained', 'total_marks', 'remarks']]
                            st.dataframe(df_grades)
                            
                            # Current course grade
                            st.write(f"Course Grade: {enrollment['grade'] or 'N/A'}")
                            st.write(f"Course Marks: {enrollment['marks'] or '0'}%")
                        else:
                            st.info("No grades yet")
                        st.markdown("---")
                else:
                    st.info("No students enrolled")
        else:
            st.info("No courses assigned")

# Dashboard functions - STUDENT
def student_dashboard():
    st.sidebar.title("🎓 Student Panel")
    
    # Get student details
    student = db.get_student_by_user_id(st.session_state.user_id)
    
    if student:
        st.sidebar.write(f"**Name:** {student['full_name']}")
        st.sidebar.write(f"**Roll Number:** {student['roll_number']}")
        st.sidebar.write(f"**Class:** {student['class_name']} - {student['section']}")
    
    menu_options = [
        "📊 Dashboard",
        "📚 My Courses",
        "📅 My Attendance",
        "📈 My Grades",
        "➕ Enroll in Courses",
        "👤 My Profile"
    ]
    menu = st.sidebar.selectbox("Navigation", menu_options)
    
    st.title(f"Student Dashboard")
    st.markdown("---")
    
    if not student:
        st.error("Student profile not found!")
        return
    
    if menu == "📊 Dashboard":
        st.subheader(f"Welcome, {student['full_name']}!")
        
        enrollments = db.get_student_enrollments(student['student_id'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Enrolled Courses", len(enrollments))
        
        with col2:
            total_credits = sum(e.get('credits', 0) for e in enrollments)
            st.metric("Total Credits", total_credits)
        
        with col3:
            if enrollments:
                total_marks = sum(e.get('marks', 0) for e in enrollments)
                avg_marks = total_marks / len(enrollments) if enrollments else 0
                st.metric("Average Marks", f"{avg_marks:.1f}%")
            else:
                st.metric("Average Marks", "N/A")
        
        with col4:
            st.metric("Class", f"{student['class_name']} - {student['section']}")
        
        # Current courses
        st.subheader("📚 Current Courses")
        if enrollments:
            df_enrollments = pd.DataFrame(enrollments)
            st.dataframe(df_enrollments[['course_code', 'course_name', 'credits', 'grade', 'marks', 'attendance_percentage']])
        else:
            st.info("No courses enrolled yet")
    
    elif menu == "📚 My Courses":
        st.subheader("My Courses")
        
        enrollments = db.get_student_enrollments(student['student_id'])
        if enrollments:
            for idx, enrollment in enumerate(enrollments):
                st.write(f"**{enrollment['course_code']} - {enrollment['course_name']}** ({enrollment['credits']} credits)")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Teacher: {enrollment['teacher_name'] or 'Not assigned'}")
                    st.write(f"Grade: {enrollment['grade'] or 'N/A'}")
                    st.write(f"Marks: {enrollment['marks'] or '0'}%")
                
                with col2:
                    st.write(f"Attendance: {enrollment['attendance_percentage'] or '0'}%")
                    st.write(f"Status: {enrollment['status']}")
                
                # Course actions
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("View Attendance", key=f"att_{idx}"):
                        attendance = db.get_student_attendance(student['student_id'], enrollment['course_id'])
                        if attendance:
                            df_attendance = pd.DataFrame(attendance)
                            st.dataframe(df_attendance[['date', 'status', 'remarks']])
                        else:
                            st.info("No attendance records")
                
                with col_btn2:
                    if st.button("View Grades", key=f"grades_{idx}"):
                        grades = db.get_student_grades(student['student_id'], enrollment['course_id'])
                        if grades:
                            df_grades = pd.DataFrame(grades)
                            st.dataframe(df_grades[['title', 'marks_obtained', 'total_marks', 'remarks']])
                        else:
                            st.info("No grades available")
                st.markdown("---")
        else:
            st.info("No courses enrolled")
    
    elif menu == "📅 My Attendance":
        st.subheader("My Attendance")
        
        enrollments = db.get_student_enrollments(student['student_id'])
        if enrollments:
            options = [f"{e['course_code']} - {e['course_name']}" for e in enrollments] + ["All Courses"]
            selected_course = st.selectbox(
                "Select Course",
                options=options
            )
            
            if selected_course:
                course_id = None
                if selected_course != "All Courses":
                    course_id = next(e['course_id'] for e in enrollments if f"{e['course_code']} - {e['course_name']}" == selected_course)
                
                attendance = db.get_student_attendance(student['student_id'], course_id)
                if attendance:
                    df_attendance = pd.DataFrame(attendance)
                    df_attendance = df_attendance[['date', 'course_code', 'course_name', 'status', 'remarks']]
                    
                    # Calculate statistics
                    total_classes = len(df_attendance)
                    present_classes = len(df_attendance[df_attendance['status'].isin(['present', 'late'])])
                    attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Classes", total_classes)
                    with col2:
                        st.metric("Present Classes", present_classes)
                    with col3:
                        st.metric("Attendance %", f"{attendance_percentage:.1f}%")
                    
                    st.dataframe(df_attendance)
                else:
                    st.info("No attendance records found")
        else:
            st.info("No courses enrolled")
    
    elif menu == "📈 My Grades":
        st.subheader("My Grades")
        
        enrollments = db.get_student_enrollments(student['student_id'])
        if enrollments:
            options = [f"{e['course_code']} - {e['course_name']}" for e in enrollments] + ["All Courses"]
            selected_course = st.selectbox(
                "Select Course",
                options=options
            )
            
            if selected_course:
                course_id = None
                if selected_course != "All Courses":
                    course_id = next(e['course_id'] for e in enrollments if f"{e['course_code']} - {e['course_name']}" == selected_course)
                
                grades = db.get_student_grades(student['student_id'], course_id)
                if grades:
                    df_grades = pd.DataFrame(grades)
                    df_grades = df_grades[['course_code', 'course_name', 'title', 'marks_obtained', 'total_marks', 'remarks']]
                    
                    # Calculate average
                    if not df_grades.empty and 'marks_obtained' in df_grades.columns and 'total_marks' in df_grades.columns:
                        total_obtained = df_grades['marks_obtained'].sum()
                        total_possible = df_grades['total_marks'].sum()
                        if total_possible > 0:
                            avg_score = (total_obtained / total_possible) * 100
                            st.metric("Average Score", f"{avg_score:.1f}%")
                    
                    st.dataframe(df_grades)
                else:
                    st.info("No grades available yet")
        else:
            st.info("No courses enrolled")
    
    elif menu == "➕ Enroll in Courses":
        st.subheader("Enroll in Courses")
        
        available_courses = db.get_available_courses_for_student(student['student_id'])
        if available_courses:
            st.write("### Available Courses")
            
            for idx, course in enumerate(available_courses):
                st.write(f"**{course['course_code']} - {course['course_name']}** ({course['credits']} credits)")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Department: {course['department']}")
                    st.write(f"Semester: {course['semester']}")
                    st.write(f"Teacher: {course['teacher_name'] or 'Not assigned'}")
                
                with col2:
                    st.write(f"Description: {course['description']}")
                    st.write(f"Max Students: {course['max_students']}")
                
                if st.button("Enroll", key=f"enroll_{idx}"):
                    if db.enroll_student_in_course(student['student_id'], course['course_id']):
                        st.success(f"Successfully enrolled in {course['course_code']}!")
                        time.sleep(1)
                        rerun_app()
                st.markdown("---")
        else:
            st.info("No available courses or you're already enrolled in all courses for your semester")
    
    elif menu == "👤 My Profile":
        st.subheader("My Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Personal Information")
            st.write(f"**Full Name:** {student['full_name']}")
            st.write(f"**Roll Number:** {student['roll_number']}")
            st.write(f"**Class:** {student['class_name']} - {student['section']}")
            st.write(f"**Email:** {student['email']}")
            st.write(f"**Date of Birth:** {student['dob'] or 'N/A'}")
        
        with col2:
            st.write("### Contact Information")
            st.write(f"**Phone:** {student['phone'] or 'N/A'}")
            st.write(f"**Address:** {student['address'] or 'N/A'}")
            st.write(f"**Guardian:** {student['guardian_name'] or 'N/A'}")
            st.write(f"**Guardian Phone:** {student['guardian_phone'] or 'N/A'}")
        
        # Update profile
        st.subheader("Update Profile")
        with st.form("update_profile_form"):
            phone = st.text_input("Phone", value=student['phone'] or "")
            address = st.text_area("Address", value=student['address'] or "")
            guardian_name = st.text_input("Guardian Name", value=student['guardian_name'] or "")
            guardian_phone = st.text_input("Guardian Phone", value=student['guardian_phone'] or "")
            
            submitted = st.form_submit_button("Update Profile")
            
            if submitted:
                # Update student details
                try:
                    cursor = db.conn.cursor()
                    cursor.execute("""
                        UPDATE students 
                        SET phone = ?, address = ?, guardian_name = ?, guardian_phone = ?
                        WHERE student_id = ?
                    """, (phone, address, guardian_name, guardian_phone, student['student_id']))
                    db.conn.commit()
                    st.success("Profile updated successfully!")
                    time.sleep(1)
                    rerun_app()
                except Exception as e:
                    st.error(f"Error updating profile: {str(e)}")

# Main application
def main():
    # Sidebar logout button
    if st.session_state.logged_in:
        with st.sidebar:
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Use JavaScript to reload the page
                st.markdown('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)
    
    # Page routing
    if not st.session_state.logged_in:
        if st.session_state.page == "login":
            login()
        elif st.session_state.page == "register":
            register()
    else:
        if st.session_state.page == "dashboard":
            if st.session_state.role == "admin":
                admin_dashboard()
            elif st.session_state.role == "teacher":
                teacher_dashboard()
            elif st.session_state.role == "student":
                student_dashboard()
        else:
            # Default to dashboard
            st.session_state.page = "dashboard"
            rerun_app()

if __name__ == "__main__":
    main()