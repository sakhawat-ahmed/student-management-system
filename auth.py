import streamlit as st
import bcrypt
from database import Database

class Authentication:
    def __init__(self):
        self.db = Database()
        
    def login(self):
        """Display login form"""
        st.title("Student Management System")
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user = self.db.authenticate_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user'] = user
                        st.session_state['role'] = user['role']
                        st.session_state['username'] = user['username']
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
    
    def logout(self):
        """Logout user"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    def check_auth(self):
        """Check if user is authenticated"""
        return st.session_state.get('logged_in', False)
    
    def get_current_user(self):
        """Get current user from session"""
        return st.session_state.get('user', None)