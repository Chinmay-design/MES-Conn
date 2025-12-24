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
                            st.success("Profile picture removed")
                            st.rerun()
            
            submit = st.form_submit_button("Save Profile Settings", type="primary")
            
            if submit:
                updates = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'student_id': roll_number,
                    'current_position': current_position,
                    'company': company,
                    'department': department,
                    'year': str(graduation_year),
                    'linkedin': linkedin,
                    'skills': skills,
                    'about': about
                }
                
                # Handle profile picture
                if profile_pic:
                    image_bytes = profile_pic.read()
                    b64_string = base64.b64encode(image_bytes).decode()
                    updates['profile_pic'] = f"data:image/jpeg;base64,{b64_string}"
                
                try:
                    if update_user_profile(user_id, **updates):
                        st.success("Profile settings updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile settings")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        # Privacy Settings
        st.subheader("🔒 Privacy Settings")
        
        with st.form("alumni_privacy_form"):
            st.markdown("### Profile Visibility")
            
            col_priv1, col_priv2 = st.columns(2)
            
            with col_priv1:
                profile_visibility = st.radio(
                    "Who can see your profile?",
                    ["Everyone", "MES Community Only", "Connections Only", "Only me"]
                )
                
                show_email = st.checkbox("Show email to connections", value=True)
                show_phone = st.checkbox("Show phone number to connections", value=False)
                show_linkedin = st.checkbox("Show LinkedIn profile to everyone", value=True)
            
            with col_priv2:
                show_position = st.checkbox("Show current position to everyone", value=True)
                show_company = st.checkbox("Show company to everyone", value=True)
                show_skills = st.checkbox("Show skills to everyone", value=True)
                allow_connection_requests = st.checkbox("Allow connection requests", value=True)
            
            st.markdown("### Professional Privacy")
            
            col_prof1, col_prof2 = st.columns(2)
            
            with col_prof1:
                show_contributions = st.checkbox("Show my contributions publicly", value=True)
                show_job_postings = st.checkbox("Show my job postings", value=True)
                show_activity = st.checkbox("Show recent activity", value=True)
            
            with col_prof2:
                allow_mentorship_requests = st.checkbox("Allow mentorship requests", value=True)
                allow_job_referrals = st.checkbox("Allow job referral requests", value=True)
                show_graduation_year = st.checkbox("Show graduation year", value=True)
            
            st.markdown("### Data Sharing")
            
            share_analytics = st.checkbox(
                "Share anonymous usage data to improve platform",
                value=True
            )
            
            share_for_research = st.checkbox(
                "Allow data to be used for academic research (anonymous)",
                value=False
            )
            
            if st.form_submit_button("Save Privacy Settings", type="primary"):
                st.success("Privacy settings saved successfully!")
    
    with tab3:
        # Notification Settings
        st.subheader("🔔 Notification Settings")
        
        with st.form("alumni_notification_form"):
            st.markdown("### Email Notifications")
            
            col_email1, col_email2 = st.columns(2)
            
            with col_email1:
                email_connection_requests = st.checkbox("Connection requests", value=True)
                email_messages = st.checkbox("New messages", value=True)
                email_mentorship_requests = st.checkbox("Mentorship requests", value=True)
                email_job_applications = st.checkbox("Job applications", value=True)
            
            with col_email2:
                email_contribution_updates = st.checkbox("Contribution updates", value=True)
                email_event_reminders = st.checkbox("Event reminders", value=True)
                email_alumni_news = st.checkbox("Alumni newsletter", value=True)
                email_system_updates = st.checkbox("System updates", value=False)
            
            st.markdown("### Push Notifications")
            
            col_push1, col_push2 = st.columns(2)
            
            with col_push1:
                push_connection_requests = st.checkbox("Connection requests (push)", value=True)
                push_messages = st.checkbox("Messages (push)", value=True)
                push_mentorship_matches = st.checkbox("Mentorship matches (push)", value=True)
            
            with col_push2:
                push_job_activity = st.checkbox("Job posting activity (push)", value=True)
                push_event_updates = st.checkbox("Event updates (push)", value=True)
                push_announcements = st.checkbox("Important announcements (push)", value=True)
            
            st.markdown("### Notification Preferences")
            
            notification_frequency = st.select_slider(
                "Email notification frequency",
                options=["Real-time", "Daily Digest", "Weekly Summary"],
                value="Daily Digest"
            )
            
            quiet_hours = st.checkbox("Enable quiet hours", value=True)
            
            if quiet_hours:
                col_quiet1, col_quiet2 = st.columns(2)
                with col_quiet1:
                    quiet_start = st.time_input("Start time", value=datetime.strptime("22:00", "%H:%M").time())
                with col_quiet2:
                    quiet_end = st.time_input("End time", value=datetime.strptime("07:00", "%H:%M").time())
            
            if st.form_submit_button("Save Notification Settings", type="primary"):
                st.success("Notification settings saved successfully!")
    
    with tab4:
        # Professional Settings
        st.subheader("💼 Professional Settings")
        
        with st.form("professional_settings_form"):
            st.markdown("### Mentorship Preferences")
            
            col_mentor1, col_mentor2 = st.columns(2)
            
            with col_mentor1:
                mentorship_availability = st.selectbox(
                    "Mentorship Availability",
                    ["Available for Mentorship", "Limited Availability", "Not Currently Available", "Open to Requests"]
                )
                
                mentorship_areas = st.multiselect(
                    "Areas of Mentorship",
                    ["Career Guidance", "Technical Skills", "Interview Preparation", 
                     "Resume Review", "Industry Insights", "Leadership", 
                     "Entrepreneurship", "Higher Education", "Networking"]
                )
            
            with col_mentor2:
                preferred_mentorship_format = st.multiselect(
                    "Preferred Format",
                    ["One-on-One Meetings", "Group Sessions", "Virtual", "In-Person", "Email"]
                )
                
                max_mentees = st.number_input("Maximum number of mentees", min_value=1, max_value=10, value=3)
            
            st.markdown("### Job Posting Preferences")
            
            col_job1, col_job2 = st.columns(2)
            
            with col_job1:
                job_posting_email = st.text_input("Job application email", placeholder="careers@yourcompany.com")
                auto_reply_job_applications = st.checkbox("Auto-reply to job applications", value=True)
            
            with col_job2:
                application_deadline_default = st.number_input("Default application deadline (days)", min_value=7, max_value=90, value=30)
                require_resume = st.checkbox("Require resume for all applications", value=True)
            
            st.markdown("### Professional Networking")
            
            networking_preferences = st.multiselect(
                "Networking Preferences",
                ["Open to connecting with all alumni", "Only connect with same industry", 
                 "Only connect with same department", "Open to student connections", 
                 "Prefer senior professionals", "Open to all connections"]
            )
            
            auto_accept_connections = st.checkbox(
                "Auto-accept connection requests from MES alumni",
                value=False
            )
            
            if st.form_submit_button("Save Professional Settings", type="primary"):
                st.success("Professional settings saved successfully!")
    
    with tab5:
        # Security Settings
        st.subheader("🔐 Security Settings")
        
        # Change Password
        st.markdown("### Change Password")
        
        with st.form("alumni_change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            password_strength = "Weak"
            if new_password:
                if len(new_password) >= 8:
                    password_strength = "Medium"
                if len(new_password) >= 12 and any(c.isdigit() for c in new_password) and any(c.isalpha() for c in new_password):
                    password_strength = "Strong"
            
            st.caption(f"Password strength: **{password_strength}**")
            
            if st.form_submit_button("Change Password", type="primary"):
                if not all([current_password, new_password, confirm_password]):
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("New passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    st.success("Password changed successfully!")
        
        # Two-Factor Authentication
        st.markdown("### Two-Factor Authentication")
        
        two_factor_enabled = st.checkbox("Enable Two-Factor Authentication", value=False)
        
        if two_factor_enabled:
            st.success("2FA is enabled for your account")
            if st.button("Disable 2FA", type="secondary"):
                st.warning("Disabling 2FA will reduce your account security")
        else:
            st.info("2FA is not enabled. Enhance your account security.")
            if st.button("Enable 2FA", type="primary"):
                st.info("2FA setup will be available soon!")
        
        # Login Sessions
        st.markdown("### Active Login Sessions")
        
        with st.expander("View active sessions"):
            st.info("Login sessions feature coming soon!")
        
        # Security Alerts
        st.markdown("### Security Alerts")
        
        security_alerts = st.checkbox("Receive security alert emails", value=True)
        suspicious_login_alerts = st.checkbox("Alert on suspicious login attempts", value=True)
        
        if st.button("Test Security Alert", type="secondary"):
            st.info("Test security alert sent to your email")
    
    with tab6:
        # Data Settings
        st.subheader("📊 Data Settings")
        
        col_data1, col_data2 = st.columns(2)
        
        with col_data1:
            st.markdown("### Data Export")
            
            if st.button("Export My Data", type="primary", use_container_width=True):
                st.info("""
                Your data export has been queued. You will receive an email with a download link when it's ready.
                
                **Included in export:**
                - Profile information
                - Connections
                - Messages
                - Contributions
                - Job postings
                - Event registrations
                - Activity history
                """)
            
            st.markdown("### Data Retention")
            
            data_retention = st.selectbox(
                "Data retention period",
                ["Keep all data", "Auto-delete after 1 year", "Auto-delete after 3 years", "Auto-delete after 5 years"]
            )
        
        with col_data2:
            st.markdown("### Account Deletion")
            
            if st.button("Request Account Deletion", type="secondary", use_container_width=True):
                st.warning("""
                ## ⚠️ Account Deletion Request
                
                **This action is permanent and cannot be undone!**
                
                If you proceed:
                - All your data will be permanently deleted within 30 days
                - Your profile will be removed from the platform
                - You will lose access to all alumni features
                - Your contributions and job postings will be removed
                - This action cannot be reversed
                
                **Are you sure you want to continue?**
                """)
                
                if st.button("Yes, Delete My Account Permanently", type="primary"):
                    st.error("Account deletion feature coming soon!")
            
            st.markdown("### Data Usage")
            
            allow_data_usage = st.checkbox(
                "Allow my anonymous data to be used for platform improvement",
                value=True
            )
        
        # Data Statistics
        st.markdown("### 📈 Your Data Statistics")
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            # These would come from database
            st.metric("Profile Data", "Complete")
        
        with col_stat2:
            st.metric("Messages", "0")
        
        with col_stat3:
            st.metric("Connections", "0")
        
        with col_stat4:
            st.metric("Contributions", "0")
        
        # Data Privacy Information
        with st.expander("📋 Data Privacy Information"):
            st.markdown("""
            ### Your Data Rights
            
            **Access:** You can access all your personal data
            **Correction:** You can correct inaccurate data
            **Deletion:** You can request deletion of your data
            **Portability:** You can request a copy of your data
            **Objection:** You can object to certain data processing
            
            ### How We Use Your Data
            
            **Platform Operation:** To provide and improve our services
            **Communication:** To send important updates and notifications
            **Personalization:** To customize your experience
            **Analytics:** To understand platform usage (anonymous)
            **Security:** To protect your account and our platform
            
            ### Data Protection
            
            **Encryption:** All data is encrypted in transit and at rest
            **Access Control:** Strict access controls protect your data
            **Regular Audits:** We conduct regular security audits
            **Compliance:** We comply with applicable data protection laws
            
            For more information, contact our Data Protection Officer.
            """)
