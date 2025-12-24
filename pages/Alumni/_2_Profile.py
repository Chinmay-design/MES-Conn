import streamlit as st
from PIL import Image
import io
import base64
from utils.database import (
    get_alumni_profile, update_user_profile,
    get_friends, get_user_by_id
)

def alumni_profile_page(user_id):
    """Alumni Profile Page"""
    st.title("👤 Alumni Profile")
    
    # Get user profile
    profile = get_alumni_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Edit Profile", "Network", "Activity"])
    
    with tab1:
        # Display profile
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Profile picture
            if profile.get('profile_pic'):
                st.image(profile['profile_pic'], width=150)
            else:
                st.image("https://via.placeholder.com/150", width=150)
            
            st.markdown(f"### {profile['first_name']} {profile['last_name']}")
            st.markdown(f"**Alumni ID:** {profile['roll_number']}")
            st.markdown(f"**Email:** {profile['email']}")
            st.markdown(f"**Phone:** {profile['phone'] or 'Not provided'}")
            
            if profile.get('linkedin'):
                st.markdown(f"[LinkedIn Profile]({profile['linkedin']})")
            
            # Quick stats
            friends = get_friends(user_id)
            st.metric("Connections", len(friends))
        
        with col2:
            # Professional Information
            st.subheader("Professional Information")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Current Position:** {profile['current_position']}")
                st.markdown(f"**Company:** {profile['company']}")
                st.markdown(f"**Department:** {profile['department']}")
            
            with col_info2:
                st.markdown(f"**Graduation Year:** {profile['graduation_year']}")
                st.markdown(f"**Joined Platform:** {profile['created_at'][:10]}")
                st.markdown(f"**Last Login:** {profile.get('last_login', 'Never')[:19]}")
            
            # Skills
            st.subheader("Skills & Expertise")
            if profile['skills']:
                skills = [skill.strip() for skill in profile['skills'].split(',')]
                for skill in skills:
                    st.markdown(f"• {skill}")
            else:
                st.info("No skills added yet")
            
            # Professional Summary
            st.subheader("Professional Summary")
            if profile['about']:
                st.markdown(profile['about'])
            else:
                st.info("No professional summary added yet")
    
    with tab2:
        # Edit Profile
        st.subheader("Edit Profile")
        
        with st.form("edit_alumni_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_first_name = st.text_input("First Name", value=profile['first_name'])
                new_email = st.text_input("Email", value=profile['email'])
                new_phone = st.text_input("Phone Number", value=profile['phone'] or "")
                new_department = st.selectbox(
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
                new_graduation_year = st.number_input(
                    "Graduation Year",
                    min_value=1990,
                    max_value=2024,
                    value=int(profile['graduation_year']) if profile['graduation_year'].isdigit() else 2020
                )
            
            with col2:
                new_last_name = st.text_input("Last Name", value=profile['last_name'])
                new_roll_number = st.text_input("Roll Number", value=profile['roll_number'])
                new_current_position = st.text_input("Current Position", value=profile['current_position'])
                new_company = st.text_input("Company/Organization", value=profile['company'])
                new_linkedin = st.text_input("LinkedIn Profile URL", value=profile.get('linkedin', ''))
                new_skills = st.text_area("Skills (comma separated)", value=profile['skills'] or "")
            
            new_about = st.text_area("Professional Summary", value=profile['about'] or "", height=150)
            
            # Profile picture upload
            profile_pic = st.file_uploader("Upload Profile Picture", type=['jpg', 'jpeg', 'png'])
            
            submit = st.form_submit_button("Save Changes", type="primary")
            
            if submit:
                updates = {
                    'first_name': new_first_name,
                    'last_name': new_last_name,
                    'email': new_email,
                    'phone': new_phone,
                    'student_id': new_roll_number,
                    'department': new_department,
                    'year': str(new_graduation_year),
                    'current_position': new_current_position,
                    'company': new_company,
                    'linkedin': new_linkedin,
                    'skills': new_skills,
                    'about': new_about
                }
                
                # Handle profile picture
                if profile_pic:
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
        # Network
        st.subheader("My Network")
        
        connections = get_friends(user_id)
        
        if connections:
            # Search and filter
            col_search1, col_search2 = st.columns(2)
            
            with col_search1:
                search_term = st.text_input("🔍 Search connections")
            
            with col_search2:
                filter_by = st.selectbox(
                    "Filter by",
                    ["All", "Alumni", "Students", "By Company", "By Department"]
                )
            
            # Filter connections
            filtered_connections = connections
            
            if search_term:
                filtered_connections = [
                    c for c in connections 
                    if search_term.lower() in c['first_name'].lower()
                    or search_term.lower() in c['last_name'].lower()
                    or search_term.lower() in c.get('company', '').lower()
                ]
            
            if filter_by == "Alumni":
                filtered_connections = [c for c in filtered_connections if c['role'] == 'alumni']
            elif filter_by == "Students":
                filtered_connections = [c for c in filtered_connections if c['role'] == 'student']
            elif filter_by == "By Company":
                # Group by company
                companies = {}
                for conn in filtered_connections:
                    company = conn.get('company', 'Unknown')
                    if company not in companies:
                        companies[company] = []
                    companies[company].append(conn)
                
                # Display by company
                for company, company_conns in companies.items():
                    with st.expander(f"{company} ({len(company_conns)})"):
                        cols = st.columns(3)
                        for idx, conn in enumerate(company_conns):
                            with cols[idx % 3]:
                                display_connection_card(conn, user_id)
                return
            
            # Display connections
            cols = st.columns(3)
            for idx, conn in enumerate(filtered_connections):
                with cols[idx % 3]:
                    display_connection_card(conn, user_id)
        else:
            st.info("You haven't made any connections yet.")
    
    with tab4:
        # Activity
        st.subheader("Recent Activity")
        
        # Contributions
        from utils.database import get_contributions
        contributions = get_contributions(alumni_id=user_id)
        
        if contributions:
            st.markdown("### 💡 Recent Contributions")
            for contrib in contributions[:5]:
                col_act1, col_act2 = st.columns([3, 1])
                with col_act1:
                    type_icons = {
                        'mentorship': '👨‍🏫',
                        'donation': '💰',
                        'workshop': '🎓',
                        'job_posting': '💼',
                        'internship': '🎯',
                        'other': '💡'
                    }
                    icon = type_icons.get(contrib['type'], '💡')
                    st.markdown(f"{icon} **{contrib['title']}**")
                    st.caption(f"Status: {contrib['status'].title()} • {contrib['created_at'][:10]}")
                with col_act2:
                    if st.button("View", key=f"view_contrib_{contrib['id']}"):
                        st.session_state.current_page = "Alumni/Contributions"
                        st.rerun()
                st.markdown("---")
        
        # Job Postings
        from utils.database import get_job_postings
        job_postings = get_job_postings(active_only=True, limit=100)
        my_jobs = [j for j in job_postings if j['posted_by'] == user_id]
        
        if my_jobs:
            st.markdown("### 💼 Recent Job Postings")
            for job in my_jobs[:3]:
                col_job1, col_job2 = st.columns([3, 1])
                with col_job1:
                    st.markdown(f"**{job['position']} at {job['company']}**")
                    st.caption(f"📍 {job['location'] or 'Remote'} • Posted: {job['created_at'][:10]}")
                with col_job2:
                    if st.button("Manage", key=f"manage_{job['id']}"):
                        st.session_state.current_page = "Alumni/Jobs"
                        st.rerun()
                st.markdown("---")
        
        # Platform Activity
        st.markdown("### 📊 Platform Activity")
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            st.metric("Total Connections", len(connections))
        
        with col_act2:
            st.metric("Contributions", len(contributions))
        
        with col_act3:
            st.metric("Jobs Posted", len(my_jobs))

def display_connection_card(conn, user_id):
    """Display a connection card"""
    with st.container():
        st.markdown(f"<div style='text-align: center; padding: 15px; border: 1px solid #e0e0e0; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
        
        if conn.get('profile_pic'):
            st.image(conn['profile_pic'], width=80)
        else:
            st.image("https://via.placeholder.com/80", width=80)
        
        st.markdown(f"**{conn['first_name']} {conn['last_name']}**")
        
        role_badge = {
            'alumni': '👨‍🎓',
            'student': '👨‍🎓',
            'admin': '👑'
        }.get(conn['role'], '👤')
        st.caption(f"{role_badge} {conn['role'].title()}")
        
        if conn.get('current_position'):
            st.caption(f"💼 {conn['current_position']}")
        
        if conn.get('company'):
            st.caption(f"🏢 {conn['company']}")
        
        if conn.get('department'):
            st.caption(f"🎓 {conn['department']}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💬", key=f"alum_chat_conn_{conn['id']}", help="Chat"):
                st.session_state.chat_with = conn['id']
                st.session_state.current_page = "Alumni/Chat"
                st.rerun()
        
        with col_btn2:
            if st.button("👁️", key=f"alum_view_conn_{conn['id']}", help="View Profile"):
                with st.expander("Connection Profile", expanded=True):
                    conn_details = get_user_by_id(conn['id'])
                    if conn_details:
                        st.write(f"**Email:** {conn_details['email']}")
                        st.write(f"**Phone:** {conn_details.get('phone', 'Not provided')}")
                        st.write(f"**Joined:** {conn_details['created_at'][:10]}")
                        if conn_details.get('skills'):
                            st.write(f"**Skills:** {conn_details['skills']}")
                        if conn_details.get('about'):
                            st.write(f"**About:** {conn_details['about']}")
        
        st.markdown("</div>", unsafe_allow_html=True)
