import streamlit as st
import base64
from PIL import Image
import io
from datetime import datetime
from utils.database import (
    get_alumni_profile, update_user_profile,
    get_user_by_id
)

def alumni_settings_page(user_id):
    """Alumni Settings Page"""
    st.title("⚙️ Alumni Settings")
    
    # Get user profile
    profile = get_alumni_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Profile", "Privacy", "Notifications", 
        "Professional", "Security", "Data"
    ])
    
    with tab1:
        # Profile Settings
        st.subheader("👤 Profile Settings")
        
        with st.form("alumni_profile_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", value=profile['first_name'])
                email = st.text_input("Email", value=profile['email'])
                phone = st.text_input("Phone Number", value=profile['phone'] or "")
                graduation_year = st.number_input(
                    "Graduation Year",
                    min_value=1990,
                    max_value=2024,
                    value=int(profile['graduation_year']) if profile['graduation_year'].isdigit() else 2020
                )
            
            with col2:
                last_name = st.text_input("Last Name", value=profile['last_name'])
                roll_number = st.text_input("Roll Number", value=profile['roll_number'])
                current_position = st.text_input("Current Position", value=profile['current_position'])
                company = st.text_input("Company", value=profile['company'])
            
            # Professional details
            st.subheader("Professional Details")
            
            col_pro1, col_pro2 = st.columns(2)
            
            with col_pro1:
                department = st.selectbox(
                    "Department",
                    ["Computer Science", "Electronics & Communication", "Mechanical", 
                     "Civil", "Electrical", "Information Technology", "Chemical", 
                     "Biotechnology", "Aerospace", "Other"],
                    index=["Computer Science", "Electronics & Communication", "Mechanical", 
                          "Civil", "Electrical", "Information Technology", "Chemical", 
                          "Biotechnology", "Aerospace", "Other"].index(profile['department']) 
                          if profile['department'] in ["Computer Science", "Electronics & Communication", "Mechanical", 
                                                     "Civil", "Electrical", "Information Technology", "Chemical", 
                                                     "Biotechnology", "Aerospace", "Other"] else 0
                )
                linkedin = st.text_input("LinkedIn Profile", value=profile.get('linkedin', ''))
            
            with col_pro2:
                skills = st.text_area("Skills", value=profile['skills'] or "")
                about = st.text_area("Professional Summary", value=profile['about'] or "", height=100)
            
            # Profile picture
            st.subheader("Profile Picture")
            profile_pic = st.file_uploader("Upload professional profile picture", type=['jpg', 'jpeg', 'png'])
            
            if profile.get('profile_pic'):
                col_pic1, col_pic2 = st.columns([1, 3])
                with col_pic1:
                    st.image(profile['profile_pic'], width=100)
                with col_pic2:
                    if st.button("Remove Profile Picture", type="secondary"):
                        if update_user_profile(user_id, profile_pic=None):
                           
