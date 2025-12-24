import streamlit as st
from utils.database import (
    get_all_users, get_friends, add_friend_request,
    get_user_by_id, get_user_statistics
)

def alumni_networking_page(user_id):
    """Alumni Networking Page"""
    st.title("🤝 Networking")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Find Alumni", "Find Students", "Mentorship", "Industry Groups"
    ])
    
    with tab1:
        # Find Alumni
        st.subheader("👨‍🎓 Find Alumni")
        
        # Search and filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            company_filter = st.text_input("Filter by company")
        
        with col_filter2:
            position_filter = st.text_input("Filter by position")
        
        with col_filter3:
            graduation_year_filter = st.selectbox(
                "Graduation Year",
                ["All"] + [str(year) for year in range(1990, 2025)][::-1]
            )
        
        # Get all alumni
        all_alumni = get_all_users(role='alumni', exclude_id=user_id)
        
        # Get existing connections
        connections = get_friends(user_id)
        connection_ids = [c['id'] for c in connections]
        
        # Filter out existing connections
        potential_connections = [a for a in all_alumni if a['id'] not in connection_ids]
        
        # Apply filters
        filtered_alumni = potential_connections
        
        if company_filter:
            filtered_alumni = [a for a in filtered_alumni if a.get('company', '').lower().find(company_filter.lower()) != -1]
        
        if position_filter:
            filtered_alumni = [a for a in filtered_alumni if a.get('current_position', '').lower().find(position_filter.lower()) != -1]
        
        if graduation_year_filter != "All":
            filtered_alumni = [a for a in filtered_alumni if a.get('year') == graduation_year_filter]
        
        # Display alumni
        if filtered_alumni:
            st.markdown(f"Found **{len(filtered_alumni)}** alumni to connect with")
            
            cols = st.columns(3)
            for idx, alum in enumerate(filtered_alumni[:9]):  # Show max 9
                with cols[idx % 3]:
                    display_alumni_card(alum, user_id)
            
            if len(filtered_alumni) > 9:
                if st.button("Load More Alumni", type="secondary"):
                    st.info("Pagination feature coming soon!")
        else:
            st.info("No alumni found with the current filters.")
    
    with tab2:
        # Find Students
        st.subheader("👨‍🎓 Find Students")
        
        # Search and filters
        col_sfilter1, col_sfilter2, col_sfilter3 = st.columns(3)
        
        with col_sfilter1:
            department_filter = st.selectbox(
                "Department",
                ["All", "Computer Science", "Electronics & Communication", "Mechanical", 
                 "Civil", "Electrical", "Information Technology", "Chemical", 
                 "Biotechnology", "Aerospace", "Other"]
            )
        
        with col_sfilter2:
            year_filter = st.selectbox(
                "Academic Year",
                ["All", "1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"]
            )
        
        with col_sfilter3:
            skills_filter = st.text_input("Skills (comma separated)")
        
        # Get all students
        all_students = get_all_users(role='student', exclude_id=user_id)
        
        # Get existing connections
        connections = get_friends(user_id)
        connection_ids = [c['id'] for c in connections]
        
        # Filter out existing connections
        potential_students = [s for s in all_students if s['id'] not in connection_ids]
        
        # Apply filters
        filtered_students = potential_students
        
        if department_filter != "All":
            filtered_students = [s for s in filtered_students if s.get('department') == department_filter]
        
        if year_filter != "All":
            filtered_students = [s for s in filtered_students if s.get('year') == year_filter]
        
        if skills_filter:
            skills_list = [skill.strip().lower() for skill in skills_filter.split(',')]
            filtered_students = [
                s for s in filtered_students 
                if s.get('skills') and any(skill in s['skills'].lower() for skill in skills_list)
            ]
        
        # Display students
        if filtered_students:
            st.markdown(f"Found **{len(filtered_students)}** students to connect with")
            
            cols = st.columns(3)
            for idx, student in enumerate(filtered_students[:9]):
                with cols[idx % 3]:
                    display_student_card(student, user_id)
        else:
            st.info("No students found with the current filters.")
    
    with tab3:
        # Mentorship
        st.subheader("👨‍🏫 Mentorship Program")
        
        col_ment1, col_ment2 = st.columns(2)
        
        with col_ment1:
            # Become a Mentor
            st.markdown("### Become a Mentor")
            
            with st.form("mentor_application_form"):
                areas_of_expertise = st.multiselect(
                    "Areas of Expertise",
                    ["Career Guidance", "Technical Skills", "Interview Preparation", 
                     "Resume Review", "Project Guidance", "Higher Education", 
                     "Entrepreneurship", "Leadership", "Other"]
                )
                
                availability = st.selectbox(
                    "Time Availability",
                    ["1-2 hours/week", "3-5 hours/week", "5+ hours/week", "As needed"]
                )
                
                preferred_students = st.multiselect(
                    "Preferred Student Types",
                    ["Freshmen", "Sophomores", "Juniors", "Seniors", 
                     "Graduating Students", "All"]
                )
                
                about_mentoring = st.text_area(
                    "Why do you want to be a mentor?",
                    placeholder="Share your motivation and what you hope to achieve..."
                )
                
                if st.form_submit_button("Apply as Mentor", type="primary"):
                    st.success("Mentor application submitted! We'll review it soon.")
        
        with col_ment2:
            # Find a Mentor
            st.markdown("### Find a Mentor")
            
            # This would show available mentors
            st.info("Mentor directory coming soon!")
            
            # Quick search
            mentor_search = st.text_input("🔍 Search for mentors by expertise")
            
            if st.button("Browse Mentors", type="primary"):
                st.info("Mentor browsing feature coming soon!")
        
        # Mentorship Resources
        st.markdown("---")
        st.subheader("📚 Mentorship Resources")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.markdown("### 🎯 Getting Started")
            st.info("Mentorship guide coming soon!")
        
        with col_res2:
            st.markdown("### 🤝 Best Practices")
            st.info("Mentorship tips coming soon!")
        
        with col_res3:
            st.markdown("### 📊 Success Stories")
            st.info("Success stories coming soon!")
    
    with tab4:
        # Industry Groups
        st.subheader("🏢 Industry Groups")
        
        # Industry statistics
        stats = get_user_statistics()
        alumni_by_department = stats.get('users_by_department', {})
        
        if alumni_by_department:
            st.markdown("### 📊 Alumni by Department")
            
            # Create a simple bar chart
            import plotly.express as px
            
            dept_data = []
            for dept, count in alumni_by_department.items():
                dept_data.append({
                    'Department': dept,
                    'Alumni Count': count
                })
            
            if dept_data:
                df = pd.DataFrame(dept_data)
                fig = px.bar(df, x='Department', y='Alumni Count', 
                           title="Alumni Distribution by Department")
                st.plotly_chart(fig, use_container_width=True)
        
        # Industry-specific groups
        st.markdown("### 👥 Industry Groups")
        
        industries = [
            ("💻 Technology", "Google, Microsoft, Amazon, etc."),
            ("🏦 Finance", "Banks, Investment firms, Fintech"),
            ("🏥 Healthcare", "Hospitals, Pharma, Medtech"),
            ("🏭 Manufacturing", "Automotive, Industrial, Consumer goods"),
            ("🎓 Education", "Universities, Schools, Edtech"),
            ("⚡ Energy", "Oil & Gas, Renewable energy"),
            ("🚚 Logistics", "Transportation, Supply chain"),
            ("🎨 Creative", "Design, Media, Entertainment")
        ]
        
        cols = st.columns(4)
        for idx, (industry, description) in enumerate(industries):
            with cols[idx % 4]:
                with st.container():
                    st.markdown(f"**{industry}**")
                    st.caption(description)
                    
                    member_count = 0  # Would need to calculate from database
                    st.metric("Members", member_count)
                    
                    if st.button(f"Join {industry.split()[0]}", key=f"join_ind_{idx}"):
                        st.info(f"Joining {industry} group...")

def display_alumni_card(alum, user_id):
    """Display an alumni card for networking"""
    with st.container():
        st.markdown(f"<div style='text-align: center; padding: 15px; border: 1px solid #e0e0e0; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
        
        if alum.get('profile_pic'):
            st.image(alum['profile_pic'], width=80)
        else:
            st.image("https://via.placeholder.com/80", width=80)
        
        st.markdown(f"**{alum['first_name']} {alum['last_name']}**")
        
        if alum.get('current_position'):
            st.caption(f"💼 {alum['current_position']}")
        
        if alum.get('company'):
            st.caption(f"🏢 {alum['company']}")
        
        if alum.get('department'):
            st.caption(f"🎓 {alum['department']} ({alum.get('year', '')})")
        
        if alum.get('skills'):
            skills_preview = ', '.join(alum['skills'].split(',')[:2])
            st.caption(f"🛠️ {skills_preview}")
        
        # Connection button
        if st.button("Connect", key=f"connect_alum_{alum['id']}", type="primary"):
            success, msg = add_friend_request(user_id, alum['id'])
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        
        # View profile button
        if st.button("View Profile", key=f"view_alum_{alum['id']}"):
            with st.expander("Alumni Profile", expanded=True):
                alum_details = get_user_by_id(alum['id'])
                if alum_details:
                    st.write(f"**Email:** {alum_details['email']}")
                    st.write(f"**Current Position:** {alum_details.get('current_position', 'Not specified')}")
                    st.write(f"**Company:** {alum_details.get('company', 'Not specified')}")
                    st.write(f"**Graduation Year:** {alum_details.get('year', 'Not specified')}")
                    st.write(f"**Department:** {alum_details.get('department', 'Not specified')}")
                    if alum_details.get('linkedin'):
                        st.write(f"**LinkedIn:** {alum_details['linkedin']}")
                    if alum_details.get('skills'):
                        st.write(f"**Skills:** {alum_details['skills']}")
                    if alum_details.get('about'):
                        st.write(f"**About:** {alum_details['about']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_student_card(student, user_id):
    """Display a student card for networking"""
    with st.container():
        st.markdown(f"<div style='text-align: center; padding: 15px; border: 1px solid #e0e0e0; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
        
        if student.get('profile_pic'):
            st.image(student['profile_pic'], width=80)
        else:
            st.image("https://via.placeholder.com/80", width=80)
        
        st.markdown(f"**{student['first_name']} {student['last_name']}**")
        
        if student.get('department'):
            st.caption(f"🎓 {student['department']}")
        
        if student.get('year'):
            st.caption(f"📚 {student['year']}")
        
        if student.get('skills'):
            skills_preview = ', '.join(student['skills'].split(',')[:2])
            st.caption(f"🛠️ {skills_preview}")
        
        # Connection button
        if st.button("Connect", key=f"connect_stu_{student['id']}", type="primary"):
            success, msg = add_friend_request(user_id, student['id'])
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        
        # Offer mentorship button
        if st.button("Offer Mentorship", key=f"mentor_{student['id']}"):
            with st.form(f"mentor_offer_{student['id']}"):
                st.write(f"Offer mentorship to {student['first_name']}")
                message = st.text_area(
                    "Message",
                    value=f"Hi {student['first_name']}, I noticed your profile and would like to offer mentorship. I have experience in your field and would be happy to help guide your career journey.",
                    height=100
                )
                
                if st.form_submit_button("Send Mentorship Offer", type="primary"):
                    st.success("Mentorship offer sent!")
        
        st.markdown("</div>", unsafe_allow_html=True)
