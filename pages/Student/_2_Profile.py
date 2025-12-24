import streamlit as st
from PIL import Image
import io
import base64
from utils.database import (
    get_student_profile, update_user_profile,
    get_friends, get_user_by_id
)

def student_profile_page(user_id):
    """Student Profile Page"""
    st.title("👤 Student Profile")
    
    # Get user profile
    profile = get_student_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Edit Profile", "Friends", "Activity"])
    
    with tab1:
        # Display profile
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Profile picture placeholder
            if profile.get('profile_pic'):
                st.image(profile['profile_pic'], width=150)
            else:
                st.image("https://via.placeholder.com/150", width=150)
            
            st.markdown(f"### {profile['first_name']} {profile['last_name']}")
            st.markdown(f"**Student ID:** {profile['student_id']}")
            st.markdown(f"**Email:** {profile['email']}")
            st.markdown(f"**Phone:** {profile['phone'] or 'Not provided'}")
            
            # Quick stats
            friends = get_friends(user_id)
            st.metric("Friends", len(friends))
        
        with col2:
            # Personal Information
            st.subheader("Personal Information")
            
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.markdown(f"**Department:** {profile['department']}")
                st.markdown(f"**Year:** {profile['year']}")
            
            with info_col2:
                st.markdown(f"**Joined:** {profile['created_at'][:10]}")
                st.markdown(f"**Last Login:** {profile.get('last_login', 'Never')[:19]}")
            
            # Skills
            st.subheader("Skills")
            if profile['skills']:
                skills = [skill.strip() for skill in profile['skills'].split(',')]
                for skill in skills:
                    st.markdown(f"• {skill}")
            else:
                st.info("No skills added yet")
            
            # About
            st.subheader("About")
            if profile['about']:
                st.markdown(profile['about'])
            else:
                st.info("No information added yet")
    
    with tab2:
        # Edit Profile
        st.subheader("Edit Profile")
        
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_first_name = st.text_input("First Name", value=profile['first_name'])
                new_email = st.text_input("Email", value=profile['email'])
                new_phone = st.text_input("Phone Number", value=profile['phone'] or "")
                new_department = st.selectbox("Department", 
                    ["Computer Science", "Electronics & Communication", "Mechanical", 
                     "Civil", "Electrical", "Information Technology", "Chemical", 
                     "Biotechnology", "Aerospace", "Other"],
                    index=["Computer Science", "Electronics & Communication", "Mechanical", 
                          "Civil", "Electrical", "Information Technology", "Chemical", 
                          "Biotechnology", "Aerospace", "Other"].index(profile['department']) 
                          if profile['department'] in ["Computer Science", "Electronics & Communication", "Mechanical", 
                                                     "Civil", "Electrical", "Information Technology", "Chemical", 
                                                     "Biotechnology", "Aerospace", "Other"] else 0)
            
            with col2:
                new_last_name = st.text_input("Last Name", value=profile['last_name'])
                new_student_id = st.text_input("Student ID", value=profile['student_id'])
                new_year = st.selectbox("Academic Year", 
                    ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"],
                    index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"].index(profile['year']) 
                    if profile['year'] in ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"] else 0)
                new_skills = st.text_area("Skills (comma separated)", value=profile['skills'] or "")
            
            new_about = st.text_area("About yourself", value=profile['about'] or "", height=150)
            
            # Profile picture upload
            profile_pic = st.file_uploader("Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
            
            submit = st.form_submit_button("Save Changes", type="primary")
            
            if submit:
                updates = {
                    'first_name': new_first_name,
                    'last_name': new_last_name,
                    'email': new_email,
                    'phone': new_phone,
                    'student_id': new_student_id,
                    'department': new_department,
                    'year': new_year,
                    'skills': new_skills,
                    'about': new_about
                }
                
                # Handle profile picture
                if profile_pic:
                    # Convert to base64 for storage
                    image_bytes = profile_pic.read()
                    b64_string = base64.b64encode(image_bytes).decode()
                    updates['profile_pic'] = f"data:image/jpeg;base64,{b64_string}"
                
                try:
                    if update_user_profile(user_id, **updates):
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        # Friends List
        st.subheader("My Friends")
        
        friends = get_friends(user_id)
        
        if friends:
            cols = st.columns(3)
            for idx, friend in enumerate(friends):
                with cols[idx % 3]:
                    with st.container():
                        if friend.get('profile_pic'):
                            st.image(friend['profile_pic'], width=100)
                        else:
                            st.image("https://via.placeholder.com/100", width=100)
                        
                        st.markdown(f"**{friend['first_name']} {friend['last_name']}**")
                        st.caption(f"{friend.get('department', '')}")
                        st.caption(f"{friend.get('current_position', '')}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Chat", key=f"chat_{friend['id']}"):
                                st.session_state.chat_with = friend['id']
                                st.session_state.current_page = "Student/Chat"
                                st.rerun()
                        with col_btn2:
                            if st.button("View", key=f"view_{friend['id']}"):
                                # Show friend details in modal
                                friend_details = get_user_by_id(friend['id'])
                                if friend_details:
                                    with st.expander("Friend Details", expanded=True):
                                        st.write(f"**Email:** {friend_details['email']}")
                                        st.write(f"**Phone:** {friend_details.get('phone', 'Not provided')}")
                                        if friend_details.get('skills'):
                                            st.write(f"**Skills:** {friend_details['skills']}")
                                        if friend_details.get('about'):
                                            st.write(f"**About:** {friend_details['about']}")
                        
                        st.markdown("---")
        else:
            st.info("You haven't added any friends yet.")
            
            # Suggest friends
            st.subheader("Suggested Friends")
            from utils.database import get_all_users
            all_users = get_all_users(role='student', exclude_id=user_id)
            
            if all_users:
                for user in all_users[:5]:
                    col_s1, col_s2 = st.columns([3, 1])
                    with col_s1:
                        st.markdown(f"**{user['first_name']} {user['last_name']}**")
                        st.caption(f"{user.get('department', '')} • {user.get('year', '')}")
                    with col_s2:
                        if st.button("Add", key=f"add_{user['id']}"):
                            from utils.database import add_friend_request
                            success, msg = add_friend_request(user_id, user['id'])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    st.markdown("---")
    
    with tab4:
        # Activity Log
        st.subheader("Recent Activity")
        
        # Get user events
        from utils.database import get_user_events
        events = get_user_events(user_id, upcoming=True)
        
        if events:
            st.markdown("### 📅 Registered Events")
            for event in events[:3]:
                with st.container():
                    st.markdown(f"**{event['title']}**")
                    st.caption(f"📅 {event['event_date']} • Status: {event['status']}")
                    st.markdown("---")
        
        # Get user confessions
        from utils.database import get_confessions
        # Note: This would need a function to get user's confessions
        
        # Recent connections
        st.markdown("### 👥 Recent Connections")
        recent_friends = get_friends(user_id)[:5]
        
        if recent_friends:
            for friend in recent_friends:
                st.markdown(f"• Connected with **{friend['first_name']} {friend['last_name']}** on {friend['friends_since'][:10]}")
        
        # Platform activity
        st.markdown("### 📊 Platform Activity")
        col_a1, col_a2, col_a3 = st.columns(3)
        
        with col_a1:
            st.metric("Messages Sent", "0")  # Would need to implement
        with col_a2:
            st.metric("Confessions Posted", "0")  # Would need to implement
        with col_a3:
            st.metric("Events Attended", "0")  # Would need to implement
