# 🎓 Student Management System

## 📋 Project Overview

The **Student Management System** is a complete web-based application designed to streamline academic administration in educational institutions. This system provides separate dashboards for administrators, teachers, and students with role-specific functionalities to manage all aspects of academic operations.

### 🔍 What This System Solves
- **For Schools/Colleges**: Digitalizes student records, attendance, and grading
- **For Teachers**: Simplifies course management and student evaluation
- **For Students**: Provides easy access to courses, assignments, and grades
- **For Administrators**: Offers comprehensive oversight and reporting

## ✨ Key Features

### **👨‍💼 Admin Features**
- ✅ **User Management**: Create/Delete Students, Teachers, Admins
- ✅ **Course Management**: Create courses and assign teachers
- ✅ **System Analytics**: Real-time statistics dashboard
- ✅ **Data Export**: Export all data to CSV files
- ✅ **Database Management**: Reset and manage system data

### **👨‍🏫 Teacher Features**
- ✅ **Course Management**: View assigned courses and students
- ✅ **Attendance Tracking**: Mark daily attendance with multiple statuses
- ✅ **Assignment Management**: Create, grade, and provide feedback on assignments
- ✅ **Student Grades**: Enter and update student marks
- ✅ **Student Monitoring**: Track student performance and progress

### **🎓 Student Features**
- ✅ **Course Enrollment**: Browse and enroll in available courses
- ✅ **Assignment Submission**: Submit assignments with text or file upload
- ✅ **Grade Viewing**: Check grades and teacher feedback
- ✅ **Attendance Tracking**: View personal attendance records
- ✅ **Profile Management**: Update personal information

## 🚀 How to Run This Project on Your Computer

### **Prerequisites**
- **Python 3.8 or higher** installed on your computer
- Basic knowledge of using command line/terminal
- Internet connection (for first-time setup)

### **Step-by-Step Installation Guide**

#### **Step 1: Download/Clone the Project**

**Option A: Download as ZIP**
1. Click the green "Code" button at the top right of this page
2. Select "Download ZIP"
3. Extract the ZIP file to a folder on your computer

**Option B: Clone using Git (Recommended)**
```bash
git clone https://github.com/yourusername/student-management-system.git
cd student-management-system
```

#### **Step 2: Set Up Virtual Environment (Recommended)**

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

*You'll know it's activated when you see `(venv)` before your command prompt*

#### **Step 3: Install Required Packages**

Make sure you're in the project folder and virtual environment is activated, then run:

```bash
pip install streamlit pandas bcrypt
```

Or create a `requirements.txt` file with:
```txt
streamlit==1.42.0
pandas==2.2.3
bcrypt==4.1.2
```

Then install using:
```bash
pip install -r requirements.txt
```

#### **Step 4: Run the Application**

```bash
streamlit run app.py
```

This will:
1. Start the web server
2. Create the database automatically
3. Open your default web browser at `http://localhost:8501`

**If browser doesn't open automatically:**
1. Open your web browser
2. Go to: `http://localhost:8501`

### **Step 5: Log In to the System**

**Default Admin Account:**
- **Username**: `admin`
- **Password**: `admin123`

**To create your own accounts:**
1. Click "Register" on the login page
2. Choose your role (Student/Teacher)
3. Fill in the registration form
4. Login with your new credentials

## 📂 Project Files Explained

| File/Folder | Purpose |
|------------|---------|
| `app.py` | Main application file - contains all the user interface |
| `database.py` | Handles all database operations and setup |
| `student_management.db` | SQLite database file (created automatically) |
| `assignments/` | Folder for storing uploaded assignment files |

## 🖥️ User Guide

### **For First-Time Users**

#### **As an Administrator:**
1. Login with `admin/admin123`
2. Go to "➕ Create New User" to create teacher/student accounts
3. Create courses in "📚 Course Management"
4. Assign teachers to courses

#### **As a Teacher:**
1. Register or ask admin to create your account
2. Login and check "📚 My Courses"
3. Create assignments for your students
4. Mark attendance and grade submissions

#### **As a Student:**
1. Register or ask admin to create your account
2. Login and enroll in courses from "➕ Enroll in Courses"
3. Submit assignments in "📝 My Assignments"
4. Check your grades and attendance

## 🔧 Troubleshooting Common Issues

### **"Module not found" error**
```bash
# Make sure you're in the project folder
cd student-management-system

# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall requirements
pip install streamlit pandas bcrypt
```

### **Port 8501 already in use**
```bash
# Run on a different port
streamlit run app.py --server.port 8502
```

### **Database issues**
```bash
# Delete the database file and restart
rm student_management.db  # On Windows: del student_management.db
streamlit run app.py
```

### **"streamlit command not found"**
```bash
# Check Python installation
python --version

# Make sure pip installed correctly
pip list | grep streamlit

# If using Python 3 specifically
python3 -m streamlit run app.py
```

## 📱 Accessing from Other Devices

If you want to access from your phone or another computer on the same network:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Then access using:
- Your computer: `http://localhost:8501`
- Other devices: `http://[YOUR-COMPUTER-IP]:8501`

Find your computer's IP address:
- **Windows**: `ipconfig` in Command Prompt
- **Mac/Linux**: `ifconfig` or `ip addr` in Terminal

## 🗂️ Managing Your Data

### **Backup Your Database**
```bash
# Copy the database file
cp student_management.db student_management_backup.db
```

### **Reset Everything**
```bash
# Delete database and restart
rm student_management.db
streamlit run app.py
```

## 📝 Customization Options

### **Change Default Admin Password**
1. Login as admin
2. Go to "⚙️ System Settings"
3. You can modify the admin password in the database

### **Add More Departments**
Edit the `app.py` file and look for department lists to add your own departments.

## 🆘 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Make sure all prerequisites are installed
3. Try resetting the database
4. Create an issue on GitHub with error details

## 🎯 Quick Start Commands Summary

```bash
# 1. Clone/download the project
git clone https://github.com/yourusername/student-management-system.git
cd student-management-system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install requirements
pip install streamlit pandas bcrypt

# 4. Run the application
streamlit run app.py

# 5. Open browser and go to:
# http://localhost:8501
# Login: admin / admin123
```

## 💡 Tips for Best Experience

1. **Use Chrome/Firefox** for best compatibility
2. **Keep the terminal open** while using the app
3. **Regularly backup** your database file
4. **Create test accounts** to explore all features
5. **Check console errors** in browser (F12) if something doesn't work

---

**🎉 You're all set!** The system is now running on your computer. Start by logging in as admin and exploring the features. The database will be created automatically in your project folder.
