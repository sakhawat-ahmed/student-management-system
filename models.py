class User:
    def __init__(self, user_id, username, password, role, email, full_name):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.email = email
        self.full_name = full_name

class Student:
    def __init__(self, student_id, user_id, roll_number, class_name, section, 
                 dob, phone, address, guardian_name, guardian_phone):
        self.student_id = student_id
        self.user_id = user_id
        self.roll_number = roll_number
        self.class_name = class_name
        self.section = section
        self.dob = dob
        self.phone = phone
        self.address = address
        self.guardian_name = guardian_name
        self.guardian_phone = guardian_phone

class Teacher:
    def __init__(self, teacher_id, user_id, employee_id, department, 
                 qualification, experience, phone, address):
        self.teacher_id = teacher_id
        self.user_id = user_id
        self.employee_id = employee_id
        self.department = department
        self.qualification = qualification
        self.experience = experience
        self.phone = phone
        self.address = address

class Course:
    def __init__(self, course_id, course_code, course_name, credits, 
                 teacher_id, class_name, description):
        self.course_id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.credits = credits
        self.teacher_id = teacher_id
        self.class_name = class_name
        self.description = description

class Attendance:
    def __init__(self, attendance_id, student_id, course_id, date, 
                 status, remarks):
        self.attendance_id = attendance_id
        self.student_id = student_id
        self.course_id = course_id
        self.date = date
        self.status = status
        self.remarks = remarks

class Grade:
    def __init__(self, grade_id, student_id, course_id, exam_type, 
                 marks, grade, remarks):
        self.grade_id = grade_id
        self.student_id = student_id
        self.course_id = course_id
        self.exam_type = exam_type
        self.marks = marks
        self.grade = grade
        self.remarks = remarks