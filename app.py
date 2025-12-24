import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import base64
from utils.database import (
    create_tables, add_user, verify_user, get_user_role,
    get_student_profile, get_alumni_profile, update_user_profile,
    get_all_users, get_confessions, add_confession,
    get_events, add_event, register_for_event,
    get_chat_messages, send_message, get_conversations,
    get_user_by_id, get_friends, add_friend_request,
    accept_friend_request, get_pending_friend_requests,
    get_groups, create_group, join_group, get_group_members,
    get_group_messages, send_group_message,
    like_confession, update_confession_status,
    get_announcements, add_announcement,
    add_contribution, get_contributions,
    get_notifications, mark_all_notifications_read,
    add_job_posting, get_job_postings, apply_for_job,
    get_user_statistics, get_platform_statistics, get_growth_data
)

# Page configuration
st.set_page_config(
    page_title="MES-Connect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Login"
if 'chat_with' not in st.session_state:
    st.session_state.chat_with = None
if 'current_group' not in st.session_state:
    st.session_state.current_group = None

# Create database tables
create_tables()

# Custom CSS
def load_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .sub-header {
            font-size: 1.8rem;
            color: #3B82F6;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 5px solid #3B82F6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success-message {
            background-color: #D1FAE5;
            color: #065F46;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            border-left: 4px solid #10B981;
        }
        .error-message {
            background-color: #FEE2E2;
            color: #991B1B;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            border-left: 4px solid #EF4444;
        }
        .info-message {
            background-color: #DBEAFE;
            color: #1E40AF;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            border-left: 4px solid #3B82F6;
        }
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            font-weight: 500;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .user-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .notification-badge {
            background-color: #EF4444;
            color: white;
            border-radius: 50%;
            padding: 2px 8px;
            font-size: 0.8rem;
            position: absolute;
            top: -5px;
            right: -5px;
        }
        .message-bubble {
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 70%;
            margin: 5px 0;
            position: relative;
        }
        .message-sent {
            background-color: #3B82F6;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        .message-received {
            background-color: #E5E7EB;
            color: #111827;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        .confession-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #E5E7EB;
        }
        .event-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 4px solid #10B981;
        }
        .group-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #8B5CF6;
        }
        .tab-content {
            padding: 1rem 0;
        }
        .st-emotion-cache-1y4p8pa {
            padding: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

def login_page():
    """Login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='main-header'>🎓 MES-Connect</h1>", unsafe_allow_html=True)
        st.markdown("### Connect. Network. Grow.")
        
        with st.container():
            st.markdown("### Login to Your Account")
            
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                login_btn = st.button("Login", type="primary", use_container_width=True)
            
            if login_btn:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        user_id = verify_user(email, password)
                        if user_id:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            st.session_state.user_role = get_user_role(user_id)
                            st.session_state.current_page = f"{st.session_state.user_role}/Dashboard"
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
            
            st.markdown("---")
            st.markdown("### New to MES-Connect?")
            
            col_sign1, col_sign2 = st.columns(2)
            with col_sign1:
                if st.button("👤 Register as Student", use_container_width=True, type="secondary"):
                    st.session_state.current_page = "Student_Signup"
                    st.rerun()
            with col_sign2:
                if st.button("👨‍🎓 Register as Alumni", use_container_width=True, type="secondary"):
                    st.session_state.current_page = "Alumni_Signup"
                    st.rerun()
            
            st.markdown("---")
            st.caption("Forgot password? Contact administrator for support.")

def student_signup_page():
    """Student registration page"""
    st.markdown("<h1 class='main-header'>Student Registration</h1>", unsafe_allow_html=True)
    
    with st.form("student_signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="John")
            email = st.text_input("Email *", placeholder="john@mes.edu")
            password = st.text_input("Password *", type="password", placeholder="Create a strong password")
            phone = st.text_input("Phone Number", placeholder="+91 9876543210")
            department = st.selectbox("Department *", 
                ["Computer Science", "Electronics & Communication", "Mechanical", 
                 "Civil", "Electrical", "Information Technology", "Chemical", 
                 "Biotechnology", "Aerospace", "Other"])
            
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Doe")
            student_id = st.text_input("Student ID *", placeholder="MES2023001")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
            year = st.selectbox("Academic Year *", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"])
            skills = st.text_area("Skills (comma separated)", placeholder="Python, Java, Web Development, Machine Learning")
        
        about = st.text_area("About yourself", placeholder="Tell us about your interests, achievements, and goals...")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submit:
            if not all([first_name, last_name, email, password, confirm_password, student_id, department, year]):
                st.error("Please fill all required fields (*)")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                try:
                    with st.spinner("Creating your account..."):
                        user_id = add_user(
                            email=email,
                            password=password,
                            role="student",
                            first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            student_id=student_id,
                            department=department,
                            year=year,
                            skills=skills,
                            about=about
                        )
                        if user_id:
                            st.success("🎉 Registration successful! Please login.")
                            st.balloons()
                            st.session_state.current_page = "Login"
                            st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
    
    col_back1, col_back2, col_back3 = st.columns([1, 2, 1])
    with col_back2:
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.current_page = "Login"
            st.rerun()

def alumni_signup_page():
    """Alumni registration page"""
    st.markdown("<h1 class='main-header'>Alumni Registration</h1>", unsafe_allow_html=True)
    
    with st.form("alumni_signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="John")
            email = st.text_input("Email *", placeholder="john.doe@company.com")
            password = st.text_input("Password *", type="password", placeholder="Create a strong password")
            phone = st.text_input("Phone Number", placeholder="+91 9876543210")
            graduation_year = st.number_input("Graduation Year *", min_value=1990, max_value=2024, step=1, value=2020)
            department = st.selectbox("Department *", 
                ["Computer Science", "Electronics & Communication", "Mechanical", 
                 "Civil", "Electrical", "Information Technology", "Chemical", 
                 "Biotechnology", "Aerospace", "Other"])
            
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Doe")
            roll_number = st.text_input("Roll Number *", placeholder="MES2016001")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
            current_position = st.text_input("Current Position *", placeholder="Software Engineer")
            company = st.text_input("Company/Organization *", placeholder="Google, Microsoft, etc.")
            skills = st.text_area("Skills (comma separated)", placeholder="Leadership, Project Management, Python, Data Analysis")
        
        about = st.text_area("Professional Summary", placeholder="Share your career journey, expertise, and achievements...")
        linkedin = st.text_input("LinkedIn Profile URL", placeholder="https://linkedin.com/in/yourprofile")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submit:
            if not all([first_name, last_name, email, password, confirm_password, roll_number, 
                       current_position, company, department]):
                st.error("Please fill all required fields (*)")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                try:
                    with st.spinner("Creating your account..."):
                        user_id = add_user(
                            email=email,
                            password=password,
                            role="alumni",
                            first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            student_id=roll_number,
                            department=department,
                            year=str(graduation_year),
                            skills=skills,
                            about=about,
                            current_position=current_position,
                            company=company,
                            linkedin=linkedin
                        )
                        if user_id:
                            st.success("🎉 Registration successful! Please login.")
                            st.balloons()
                            st.session_state.current_page = "Login"
                            st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
    
    col_back1, col_back2, col_back3 = st.columns([1, 2, 1])
    with col_back2:
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.current_page = "Login"
            st.rerun()

def logout():
    """Logout function"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.current_page = "Login"
    st.session_state.chat_with = None
    st.session_state.current_group = None
    st.rerun()

def display_notifications():
    """Display notifications in sidebar"""
    notifications = get_notifications(st.session_state.user_id, unread_only=True)
    if notifications:
        st.sidebar.markdown("### 🔔 Notifications")
        for notif in notifications[:5]:  # Show only 5 latest
            with st.sidebar.container():
                col1, col2 = st.sidebar.columns([4, 1])
                with col1:
                    st.sidebar.markdown(f"**{notif['title']}**")
                    st.sidebar.caption(notif['message'][:50] + "...")
                with col2:
                    if st.sidebar.button("✓", key=f"read_{notif['id']}"):
                        mark_all_notifications_read(st.session_state.user_id)
                        st.rerun()
                st.sidebar.markdown("---")
        
        if len(notifications) > 5:
            if st.sidebar.button("View All Notifications"):
                # You can implement a notifications page
                st.info("Notifications page coming soon!")

def main():
    """Main application controller"""
    if not st.session_state.logged_in:
        if st.session_state.current_page == "Login":
            login_page()
        elif st.session_state.current_page == "Student_Signup":
            student_signup_page()
        elif st.session_state.current_page == "Alumni_Signup":
            alumni_signup_page()
    else:
        # Display sidebar with navigation
        with st.sidebar:
            # User info
            user = get_user_by_id(st.session_state.user_id)
            if user:
                st.markdown(f"<div class='user-card'>", unsafe_allow_html=True)
                st.markdown(f"### 👤 {user['first_name']} {user['last_name']}")
                st.markdown(f"**{user['role'].title()}**")
                if user['department']:
                    st.markdown(f"🎓 {user['department']}")
                if user['current_position'] and user['company']:
                    st.markdown(f"🏢 {user['current_position']} at {user['company']}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation based on role
            pages = []
            if st.session_state.user_role == "student":
                pages = [
                    ("🏠 Dashboard", "Student/Dashboard"),
                    ("👤 Profile", "Student/Profile"),
                    ("👥 Friends", "Student/Friends"),
                    ("💬 Chat", "Student/Chat"),
                    ("👥 Groups", "Student/Groups"),
                    ("📝 Confessions", "Student/Confessions"),
                    ("📅 Events", "Student/Events"),
                    ("💼 Jobs", "Student/Jobs"),
                    ("⚙️ Settings", "Student/Settings")
                ]
            elif st.session_state.user_role == "alumni":
                pages = [
                    ("🏠 Dashboard", "Alumni/Dashboard"),
                    ("👤 Profile", "Alumni/Profile"),
                    ("🤝 Networking", "Alumni/Networking"),
                    ("💬 Chat", "Alumni/Chat"),
                    ("👥 Groups", "Alumni/Groups"),
                    ("📅 Events", "Alumni/Events"),
                    ("💡 Contributions", "Alumni/Contributions"),
                    ("💼 Jobs", "Alumni/Jobs"),
                    ("⚙️ Settings", "Alumni/Settings")
                ]
            elif st.session_state.user_role == "admin":
                pages = [
                    ("🏠 Dashboard", "Admin/Dashboard"),
                    ("👨‍🎓 Student Management", "Admin/Student_Management"),
                    ("👨‍🎓 Alumni Management", "Admin/Alumni_Management"),
                    ("📢 Announcements", "Admin/Announcements"),
                    ("🔍 Confession Moderation", "Admin/Confession_Moderation"),
                    ("👥 Groups Management", "Admin/Groups_Management"),
                    ("📊 Analytics", "Admin/Analytics"),
                    ("⚙️ System Settings", "Admin/Settings")
                ]
            
            st.markdown("### 📍 Navigation")
            for page_name, page_key in pages:
                if st.button(page_name, key=page_key, use_container_width=True):
                    st.session_state.current_page = page_key
                    st.session_state.chat_with = None
                    st.session_state.current_group = None
                    st.rerun()
            
            # Display notifications
            display_notifications()
            
            st.markdown("---")
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                logout()
        
        # Load the current page
        try:
            if "Student/Dashboard" in st.session_state.current_page:
                from pages.Student._1_Dashboard import student_dashboard_page
                student_dashboard_page(st.session_state.user_id)
            elif "Student/Profile" in st.session_state.current_page:
                from pages.Student._2_Profile import student_profile_page
                student_profile_page(st.session_state.user_id)
            elif "Student/Friends" in st.session_state.current_page:
                from pages.Student._3_Friends import student_friends_page
                student_friends_page(st.session_state.user_id)
            elif "Student/Chat" in st.session_state.current_page:
                from pages.Student._4_Chat import student_chat_page
                student_chat_page(st.session_state.user_id)
            elif "Student/Groups" in st.session_state.current_page:
                from pages.Student._5_Groups import student_groups_page
                student_groups_page(st.session_state.user_id)
            elif "Student/Confessions" in st.session_state.current_page:
                from pages.Student._6_Confessions import student_confessions_page
                student_confessions_page(st.session_state.user_id)
            elif "Student/Events" in st.session_state.current_page:
                from pages.Student._7_Events import student_events_page
                student_events_page(st.session_state.user_id)
            elif "Student/Jobs" in st.session_state.current_page:
                from pages.Student._Jobs import student_jobs_page
                student_jobs_page(st.session_state.user_id)
            elif "Student/Settings" in st.session_state.current_page:
                from pages.Student._8_Settings import student_settings_page
                student_settings_page(st.session_state.user_id)
            elif "Alumni/Dashboard" in st.session_state.current_page:
                from pages.Alumni._1_Dashboard import alumni_dashboard_page
                alumni_dashboard_page(st.session_state.user_id)
            elif "Alumni/Profile" in st.session_state.current_page:
                from pages.Alumni._2_Profile import alumni_profile_page
                alumni_profile_page(st.session_state.user_id)
            elif "Alumni/Networking" in st.session_state.current_page:
                from pages.Alumni._3_Networking import alumni_networking_page
                alumni_networking_page(st.session_state.user_id)
            elif "Alumni/Chat" in st.session_state.current_page:
                from pages.Alumni._4_Chat import alumni_chat_page
                alumni_chat_page(st.session_state.user_id)
            elif "Alumni/Groups" in st.session_state.current_page:
                from pages.Alumni._5_Groups import alumni_groups_page
                alumni_groups_page(st.session_state.user_id)
            elif "Alumni/Events" in st.session_state.current_page:
                from pages.Alumni._6_Events import alumni_events_page
                alumni_events_page(st.session_state.user_id)
            elif "Alumni/Contributions" in st.session_state.current_page:
                from pages.Alumni._7_Contributions import alumni_contributions_page
                alumni_contributions_page(st.session_state.user_id)
            elif "Alumni/Jobs" in st.session_state.current_page:
                from pages.Alumni._Jobs import alumni_jobs_page
                alumni_jobs_page(st.session_state.user_id)
            elif "Alumni/Settings" in st.session_state.current_page:
                from pages.Alumni._8_Settings import alumni_settings_page
                alumni_settings_page(st.session_state.user_id)
            elif "Admin/Dashboard" in st.session_state.current_page:
                from pages.Admin._1_Dashboard import admin_dashboard_page
                admin_dashboard_page()
            elif "Admin/Student_Management" in st.session_state.current_page:
                from pages.Admin._2_Student_Management import admin_student_management_page
                admin_student_management_page()
            elif "Admin/Alumni_Management" in st.session_state.current_page:
                from pages.Admin._3_Alumni_Management import admin_alumni_management_page
                admin_alumni_management_page()
            elif "Admin/Announcements" in st.session_state.current_page:
                from pages.Admin._4_Announcements import admin_announcements_page
                admin_announcements_page()
            elif "Admin/Confession_Moderation" in st.session_state.current_page:
                from pages.Admin._5_Confession_Moderation import admin_confession_moderation_page
                admin_confession_moderation_page()
            elif "Admin/Groups_Management" in st.session_state.current_page:
                from pages.Admin._6_Groups_Management import admin_groups_management_page
                admin_groups_management_page()
            elif "Admin/Analytics" in st.session_state.current_page:
                from pages.Admin._7_Analytics import admin_analytics_page
                admin_analytics_page()
            elif "Admin/Settings" in st.session_state.current_page:
                from pages.Admin._8_Settings import admin_settings_page
                admin_settings_page()
        except ImportError as e:
            st.error(f"Page not implemented yet: {e}")
            st.info("This page is under development.")

if __name__ == "__main__":
    main()
