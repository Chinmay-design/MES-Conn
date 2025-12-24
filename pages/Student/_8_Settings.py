import streamlit as st
import base64
from PIL import Image
import io
from utils.database import (
    get_student_profile, update_user_profile,
    get_user_by_id
)

def student_settings_page(user_id):
    """Student Settings Page"""
    st.title("⚙️ Settings")
    
    # Get user profile
    profile = get_student_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Account", "Privacy", "Notifications", 
        "Appearance", "Security"
    ])
    
    with tab1:
        # Account Settings
        st.subheader("👤 Account Settings")
        
        with st.form("account_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", value=profile['first_name'])
                email = st.text_input("Email", value=profile['email'])
                phone = st.text_input("Phone Number", value=profile['phone'] or "")
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
            
            with col2:
                last_name = st.text_input("Last Name", value=profile['last_name'])
                student_id = st.text_input("Student ID", value=profile['student_id'])
                year = st.selectbox(
                    "Academic Year",
                    ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"],
                    index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"].index(profile['year']) 
                    if profile['year'] in ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"] else 0
                )
                skills = st.text_area("Skills", value=profile['skills'] or "")
            
            about = st.text_area("About", value=profile['about'] or "", height=100)
            
            # Profile picture
            st.subheader("Profile Picture")
            profile_pic = st.file_uploader("Upload new profile picture", type=['jpg', 'jpeg', 'png'])
            
            if profile.get('profile_pic'):
                col_pic1, col_pic2 = st.columns([1, 3])
                with col_pic1:
                    st.image(profile['profile_pic'], width=100)
                with col_pic2:
                    if st.button("Remove Profile Picture", type="secondary"):
                        if update_user_profile(user_id, profile_pic=None):
                            st.success("Profile picture removed")
                            st.rerun()
            
            submit = st.form_submit_button("Save Changes", type="primary")
            
            if submit:
                updates = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'student_id': student_id,
                    'department': department,
                    'year': year,
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
                        st.success("Account settings updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update account settings")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        # Privacy Settings
        st.subheader("🔒 Privacy Settings")
        
        with st.form("privacy_settings_form"):
            st.markdown("### Profile Visibility")
            
            col_priv1, col_priv2 = st.columns(2)
            
            with col_priv1:
                profile_visibility = st.radio(
                    "Who can see your profile?",
                    ["Everyone", "Friends only", "Only me"]
                )
                
                show_email = st.checkbox("Show email to friends", value=True)
                show_phone = st.checkbox("Show phone number to friends", value=False)
            
            with col_priv2:
                show_skills = st.checkbox("Show skills to everyone", value=True)
                show_about = st.checkbox("Show 'About' section to everyone", value=True)
                allow_friend_requests = st.checkbox("Allow friend requests", value=True)
            
            st.markdown("### Activity Privacy")
            
            col_act1, col_act2 = st.columns(2)
            
            with col_act1:
                show_online_status = st.checkbox("Show when I'm online", value=True)
                show_last_seen = st.checkbox("Show last seen time", value=True)
                show_activity = st.checkbox("Show recent activity", value=True)
            
            with col_act2:
                allow_tagging = st.checkbox("Allow others to tag me", value=True)
                allow_sharing = st.checkbox("Allow sharing my posts", value=True)
                show_birthday = st.checkbox("Show birthday", value=False)
            
            st.markdown("### Data Sharing")
            
            allow_analytics = st.checkbox(
                "Allow anonymous usage analytics",
                value=True,
                help="Help us improve the platform by sharing anonymous usage data"
            )
            
            allow_personalization = st.checkbox(
                "Allow personalized content and recommendations",
                value=True
            )
            
            if st.form_submit_button("Save Privacy Settings", type="primary"):
                st.success("Privacy settings saved successfully!")
                # Note: These would need to be stored in the database
    
    with tab3:
        # Notification Settings
        st.subheader("🔔 Notification Settings")
        
        with st.form("notification_settings_form"):
            st.markdown("### Email Notifications")
            
            col_notif1, col_notif2 = st.columns(2)
            
            with col_notif1:
                email_friend_requests = st.checkbox("Friend requests", value=True)
                email_messages = st.checkbox("New messages", value=True)
                email_event_reminders = st.checkbox("Event reminders", value=True)
            
            with col_notif2:
                email_announcements = st.checkbox("Announcements", value=True)
                email_job_alerts = st.checkbox("Job alerts", value=True)
                email_newsletter = st.checkbox("Monthly newsletter", value=False)
            
            st.markdown("### Push Notifications")
            
            col_push1, col_push2 = st.columns(2)
            
            with col_push1:
                push_friend_requests = st.checkbox("Friend requests (push)", value=True)
                push_messages = st.checkbox("New messages (push)", value=True)
                push_event_updates = st.checkbox("Event updates (push)", value=True)
            
            with col_push2:
                push_confession_likes = st.checkbox("Confession likes (push)", value=False)
                push_group_activity = st.checkbox("Group activity (push)", value=True)
                push_system_alerts = st.checkbox("System alerts (push)", value=True)
            
            st.markdown("### Notification Frequency")
            
            notification_frequency = st.select_slider(
                "How often should we send you email notifications?",
                options=["Immediate", "Hourly", "Daily", "Weekly"],
                value="Daily"
            )
            
            quiet_hours = st.checkbox("Enable quiet hours", value=False)
            
            if quiet_hours:
                col_quiet1, col_quiet2 = st.columns(2)
                with col_quiet1:
                    quiet_start = st.time_input("Start time", value=datetime.strptime("22:00", "%H:%M").time())
                with col_quiet2:
                    quiet_end = st.time_input("End time", value=datetime.strptime("07:00", "%H:%M").time())
            
            if st.form_submit_button("Save Notification Settings", type="primary"):
                st.success("Notification settings saved successfully!")
    
    with tab4:
        # Appearance Settings
        st.subheader("🎨 Appearance Settings")
        
        col_app1, col_app2 = st.columns(2)
        
        with col_app1:
            st.markdown("### Theme")
            
            theme = st.radio(
                "Select theme",
                ["Light", "Dark", "Auto (System)"],
                index=0
            )
            
            accent_color = st.color_picker(
                "Accent Color",
                "#3B82F6"
            )
            
            font_size = st.select_slider(
                "Font Size",
                options=["Small", "Medium", "Large", "Extra Large"],
                value="Medium"
            )
        
        with col_app2:
            st.markdown("### Layout")
            
            density = st.radio(
                "Layout Density",
                ["Comfortable", "Compact"],
                index=0
            )
            
            sidebar_position = st.radio(
                "Sidebar Position",
                ["Left", "Right"],
                index=0
            )
            
            animations = st.checkbox("Enable animations", value=True)
        
        st.markdown("### Preview")
        
        # Preview section
        with st.container():
            st.markdown(f"""
            <div style="padding: 20px; border-radius: 10px; background-color: {'#1e1e1e' if theme == 'Dark' else '#ffffff'}; color: {'#ffffff' if theme == 'Dark' else '#000000'};">
                <h3 style="color: {accent_color};">Preview</h3>
                <p>This is how your interface will look with the selected settings.</p>
                <button style="background-color: {accent_color}; color: white; padding: 10px 20px; border: none; border-radius: 5px;">Sample Button</button>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Apply Appearance Settings", type="primary"):
            st.success("Appearance settings applied!")
            st.info("Some changes may require a page refresh to take effect.")
    
    with tab5:
        # Security Settings
        st.subheader("🔐 Security Settings")
        
        # Change Password
        st.markdown("### Change Password")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password", type="primary"):
                if not all([current_password, new_password, confirm_password]):
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("New passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    st.success("Password changed successfully!")
                    # Note: This would need proper implementation
        
        # Two-Factor Authentication
        st.markdown("### Two-Factor Authentication")
        
        two_factor = st.checkbox(
            "Enable Two-Factor Authentication",
            value=False,
            help="Add an extra layer of security to your account"
        )
        
        if two_factor:
            st.info("Two-factor authentication setup will be available soon!")
        
        # Login Sessions
        st.markdown("### Active Login Sessions")
        
        with st.expander("View active sessions"):
            st.info("Login sessions feature coming soon!")
            # Would show current and previous login sessions
        
        # Account Deactivation
        st.markdown("### Account Management")
        
        col_acc1, col_acc2 = st.columns(2)
        
        with col_acc1:
            if st.button("Download My Data", type="secondary", use_container_width=True):
                st.info("Data download feature coming soon!")
        
        with col_acc2:
            if st.button("Request Account Deletion", type="secondary", use_container_width=True):
                st.warning("""
                ### ⚠️ Account Deletion Request
                
                **This action cannot be undone!**
                
                If you proceed:
                - All your data will be permanently deleted
                - You will lose access to all features
                - Your profile will be removed
                - You cannot recover your account
                
                Are you sure you want to continue?
                """)
                
                if st.button("Yes, Delete My Account", type="primary"):
                    st.error("Account deletion feature coming soon!")
        
        # Security Tips
        st.markdown("### 💡 Security Tips")
        
        with st.expander("View security tips"):
            st.markdown("""
            1. **Use a strong password** - Mix letters, numbers, and symbols
            2. **Don't reuse passwords** - Use unique passwords for different accounts
            3. **Enable 2FA** - Add an extra layer of security
            4. **Log out from shared devices** - Always log out when using public computers
            5. **Be cautious with links** - Don't click suspicious links in messages
            6. **Keep software updated** - Ensure your browser and OS are up-to-date
            7. **Report suspicious activity** - Contact support if you notice anything unusual
            """)
