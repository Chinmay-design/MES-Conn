import streamlit as st
import pandas as pd
from utils.database import (
    get_all_users, get_user_by_id, update_user_profile
)

def admin_alumni_management_page():
    """Alumni Management Page for Admin"""
    st.title("👨‍🎓 Alumni Management")
    
    # Get all alumni
    all_users = get_all_users()
    alumni = [u for u in all_users if u['role'] == 'alumni']
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["All Alumni", "Add Alumni", "Alumni Analytics"])
    
    with tab1:
        # All Alumni
        st.subheader("📋 All Alumni")
        
        # Search and filters
        col_search1, col_search2, col_search3 = st.columns(3)
        
        with col_search1:
            search_term = st.text_input("🔍 Search alumni")
        
        with col_search2:
            company_filter = st.text_input("Filter by company")
        
        with col_search3:
            graduation_year_filter = st.selectbox(
                "Graduation Year",
                ["All"] + list(set([a.get('year', '') for a in alumni if a.get('year')]))
            )
        
        # Apply filters
        filtered_alumni = alumni
        
        if search_term:
            filtered_alumni = [
                a for a in filtered_alumni 
                if search_term.lower() in a['first_name'].lower()
                or search_term.lower() in a['last_name'].lower()
                or search_term.lower() in a['email'].lower()
                or search_term.lower() in a.get('company', '').lower()
            ]
        
        if company_filter:
            filtered_alumni = [a for a in filtered_alumni if company_filter.lower() in a.get('company', '').lower()]
        
        if graduation_year_filter != "All":
            filtered_alumni = [a for a in filtered_alumni if a.get('year') == graduation_year_filter]
        
        # Display alumni
        if filtered_alumni:
            st.markdown(f"**Total Alumni:** {len(filtered_alumni)}")
            
            # Create a DataFrame for better display
            df_data = []
            for alum in filtered_alumni:
                df_data.append({
                    'ID': alum['id'],
                    'Name': f"{alum['first_name']} {alum['last_name']}",
                    'Email': alum['email'],
                    'Company': alum.get('company', ''),
                    'Position': alum.get('current_position', ''),
                    'Department': alum.get('department', ''),
                    'Grad Year': alum.get('year', ''),
                    'Joined': alum['created_at'][:10]
                })
            
            df = pd.DataFrame(df_data)
            
            # Display as table with actions
            st.dataframe(
                df,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Company": st.column_config.TextColumn("Company", width="medium"),
                    "Position": st.column_config.TextColumn("Position", width="medium"),
                    "Department": st.column_config.TextColumn("Department", width="medium"),
                    "Grad Year": st.column_config.TextColumn("Grad Year", width="small"),
                    "Joined": st.column_config.TextColumn("Joined", width="small"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Alumni actions
            st.subheader("🎯 Alumni Actions")
            
            selected_id = st.selectbox(
                "Select Alumni ID to Manage",
                options=[a['id'] for a in filtered_alumni],
                format_func=lambda x: f"ID {x} - {next((a['first_name'] + ' ' + a['last_name'] for a in filtered_alumni if a['id'] == x), '')}"
            )
            
            if selected_id:
                selected_alum = next((a for a in filtered_alumni if a['id'] == selected_id), None)
                
                if selected_alum:
                    # Display alumni details
                    with st.expander(f"Details for {selected_alum['first_name']} {selected_alum['last_name']}", expanded=True):
                        col_detail1, col_detail2 = st.columns(2)
                        
                        with col_detail1:
                            st.markdown(f"**Email:** {selected_alum['email']}")
                            st.markdown(f"**Phone:** {selected_alum.get('phone', 'Not provided')}")
                            st.markdown(f"**Company:** {selected_alum.get('company', '')}")
                            st.markdown(f"**Position:** {selected_alum.get('current_position', '')}")
                        
                        with col_detail2:
                            st.markdown(f"**Department:** {selected_alum.get('department', '')}")
                            st.markdown(f"**Graduation Year:** {selected_alum.get('year', '')}")
                            st.markdown(f"**Joined:** {selected_alum['created_at'][:10]}")
                            st.markdown(f"**Last Login:** {selected_alum.get('last_login', 'Never')[:19]}")
                            if selected_alum.get('linkedin'):
                                st.markdown(f"**LinkedIn:** {selected_alum['linkedin']}")
                        
                        # Contributions summary
                        from utils.database import get_contributions
                        contributions = get_contributions(alumni_id=selected_id)
                        
                        if contributions:
                            st.markdown(f"### 💡 Contributions ({len(contributions)})")
                            for contrib in contributions[:3]:  # Show first 3
                                type_icons = {
                                    'mentorship': '👨‍🏫',
                                    'job_posting': '💼',
                                    'workshop': '🎓',
                                    'donation': '💰',
                                    'internship': '🎯',
                                    'other': '💡'
                                }
                                icon = type_icons.get(contrib['type'], '💡')
                                st.markdown(f"{icon} **{contrib['title']}** - {contrib['status'].title()}")
                        
                        # Management actions
                        st.markdown("### ⚙️ Management Actions")
                        
                        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
                        
                        with col_action1:
                            if st.button("Edit Profile", key=f"edit_alum_{selected_id}"):
                                st.session_state.edit_alumni_id = selected_id
                                st.rerun()
                        
                        with col_action2:
                            if st.button("View Contributions", key=f"contrib_{selected_id}"):
                                st.info(f"Contribution details for {selected_alum['first_name']} coming soon!")
                        
                        with col_action3:
                            if st.button("Contact", key=f"contact_{selected_id}"):
                                st.info(f"Contact {selected_alum['first_name']} coming soon!")
                        
                        with col_action4:
                            if st.button("Deactivate", key=f"deactivate_alum_{selected_id}", type="secondary"):
                                st.warning(f"Deactivate {selected_alum['first_name']}?")
                                if st.button("Confirm Deactivation", key=f"confirm_deact_alum_{selected_id}"):
                                    if update_user_profile(selected_id, is_verified=0):
                                        st.success(f"{selected_alum['first_name']} deactivated")
                                        st.rerun()
                                    else:
                                        st.error("Failed to deactivate alumni")
        else:
            st.info("No alumni found with the current filters.")
    
    with tab2:
        # Add Alumni
        st.subheader("👤 Add New Alumni")
        
        with st.form("add_alumni_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *")
                email = st.text_input("Email *")
                password = st.text_input("Password *", type="password")
                phone = st.text_input("Phone Number")
                graduation_year = st.number_input("Graduation Year *", min_value=1990, max_value=2024, step=1, value=2020)
                department = st.selectbox("Department *", 
                    ["Computer Science", "Electronics & Communication", "Mechanical", 
                     "Civil", "Electrical", "Information Technology", "Chemical", 
                     "Biotechnology", "Aerospace", "Other"])
            
            with col2:
                last_name = st.text_input("Last Name *")
                roll_number = st.text_input("Roll Number *")
                confirm_password = st.text_input("Confirm Password *", type="password")
                current_position = st.text_input("Current Position *")
                company = st.text_input("Company/Organization *")
                linkedin = st.text_input("LinkedIn Profile URL")
            
            skills = st.text_area("Skills (comma separated)")
            about = st.text_area("Professional Summary")
            
            submit = st.form_submit_button("Add Alumni", type="primary")
            
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
                        from utils.database import add_user
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
                            linkedin=linkedin,
                            is_verified=1  # Auto-verify for admin-added users
                        )
                        if user_id:
                            st.success(f"Alumni {first_name} {last_name} added successfully!")
                            st.balloons()
                        else:
                            st.error("Failed to add alumni")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab3:
        # Alumni Analytics
        st.subheader("📊 Alumni Analytics")
        
        if alumni:
            # Overall stats
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_alumni = len(alumni)
                st.metric("Total Alumni", total_alumni)
            
            with col_stat2:
                # Active alumni (logged in last 30 days)
                active_alumni = len([a for a in alumni if a.get('last_login') and 
                                   (pd.Timestamp.now() - pd.Timestamp(a['last_login'])).days <= 30])
                st.metric("Active Alumni", active_alumni)
            
            with col_stat3:
                # Alumni with contributions
                from utils.database import get_contributions
                contributing_alumni = set()
                all_contributions = get_contributions()
                for contrib in all_contributions:
                    contributing_alumni.add(contrib['alumni_id'])
                st.metric("Contributing Alumni", len(contributing_alumni))
            
            with col_stat4:
                # Average contributions per alumni
                avg_contributions = len(all_contributions) / len(contributing_alumni) if contributing_alumni else 0
                st.metric("Avg Contributions", f"{avg_contributions:.1f}")
            
            # Company distribution
            st.markdown("### 🏢 Company Distribution")
            
            company_counts = {}
            for alum in alumni:
                company = alum.get('company', 'Unknown')
                if company:
                    company_counts[company] = company_counts.get(company, 0) + 1
            
            if company_counts:
                # Get top 10 companies
                top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                import plotly.express as px
                
                df_companies = pd.DataFrame(top_companies, columns=['Company', 'Count'])
                fig = px.bar(df_companies, x='Company', y='Count',
                           title="Top Companies by Alumni Count")
                st.plotly_chart(fig, use_container_width=True)
            
            # Graduation year distribution
            st.markdown("### 🎓 Graduation Year Distribution")
            
            year_counts = {}
            for alum in alumni:
                year = alum.get('year', 'Unknown')
                if year:
                    year_counts[year] = year_counts.get(year, 0) + 1
            
            if year_counts:
                df_years = pd.DataFrame(list(year_counts.items()), columns=['Year', 'Count'])
                df_years = df_years.sort_values('Year')
                
                fig = px.line(df_years, x='Year', y='Count',
                            title="Alumni by Graduation Year",
                            markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            # Department distribution
            st.markdown("### 📚 Department Distribution")
            
            dept_counts = {}
            for alum in alumni:
                dept = alum.get('department', 'Unknown')
                if dept:
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            if dept_counts:
                df_depts = pd.DataFrame(list(dept_counts.items()), columns=['Department', 'Count'])
                
                fig = px.pie(df_depts, values='Count', names='Department',
                           title="Alumni by Department")
                st.plotly_chart(fig, use_container_width=True)
            
            # Geographic distribution (if location data available)
            st.markdown("### 🌍 Geographic Insights")
            
            # This would require location data in profiles
            st.info("Geographic analytics will be available when alumni add location information.")
            
            # Engagement metrics
            st.markdown("### 📈 Engagement Metrics")
            
            col_eng1, col_eng2, col_eng3 = st.columns(3)
            
            with col_eng1:
                # Average time on platform (placeholder)
                avg_time = "12m"
                st.metric("Avg Session Time", avg_time)
            
            with col_eng2:
                # Monthly active alumni
                mau = len([a for a in alumni if a.get('last_login') and 
                          (pd.Timestamp.now() - pd.Timestamp(a['last_login'])).days <= 30])
                st.metric("Monthly Active", mau)
            
            with col_eng3:
                # Contribution rate
                contrib_rate = (len(contributing_alumni) / total_alumni * 100) if total_alumni > 0 else 0
                st.metric("Contribution Rate", f"{contrib_rate:.1f}%")
        else:
            st.info("No alumni data available for analytics.")
    
    # Edit Alumni Modal (if triggered)
    if 'edit_alumni_id' in st.session_state:
        alum = get_user_by_id(st.session_state.edit_alumni_id)
        
        if alum:
            with st.form("edit_alumni_modal"):
                st.subheader(f"✏️ Edit Alumni: {alum['first_name']} {alum['last_name']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_first_name = st.text_input("First Name", value=alum['first_name'])
                    edit_email = st.text_input("Email", value=alum['email'])
                    edit_phone = st.text_input("Phone", value=alum.get('phone', ''))
                    edit_company = st.text_input("Company", value=alum.get('company', ''))
                    edit_department = st.selectbox(
                        "Department",
                        ["Computer Science", "Electronics & Communication", "Mechanical", 
                         "Civil", "Electrical", "Information Technology", "Chemical", 
                         "Biotechnology", "Aerospace", "Other"],
                        index=["Computer Science", "Electronics & Communication", "Mechanical", 
                              "Civil", "Electrical", "Information Technology", "Chemical", 
                              "Biotechnology", "Aerospace", "Other"].index(alum.get('department', 'Computer Science')) 
                              if alum.get('department') in ["Computer Science", "Electronics & Communication", "Mechanical", 
                                                           "Civil", "Electrical", "Information Technology", "Chemical", 
                                                           "Biotechnology", "Aerospace", "Other"] else 0
                    )
                
                with col2:
                    edit_last_name = st.text_input("Last Name", value=alum['last_name'])
                    edit_roll_number = st.text_input("Roll Number", value=alum.get('student_id', ''))
                    edit_position = st.text_input("Current Position", value=alum.get('current_position', ''))
                    edit_graduation_year = st.number_input(
                        "Graduation Year",
                        min_value=1990,
                        max_value=2024,
                        value=int(alum.get('year', 2020)) if alum.get('year', '').isdigit() else 2020
                    )
                    edit_linkedin = st.text_input("LinkedIn", value=alum.get('linkedin', ''))
                
                edit_skills = st.text_area("Skills", value=alum.get('skills', ''))
                edit_about = st.text_area("Professional Summary", value=alum.get('about', ''), height=100)
                
                # Verification status
                is_verified = st.checkbox("Account Verified", value=bool(alum.get('is_verified', 1)))
                
                col_submit1, col_submit2 = st.columns([1, 1])
                with col_submit1:
                    save = st.form_submit_button("Save Changes", type="primary")
                with col_submit2:
                    cancel = st.form_submit_button("Cancel")
                
                if save:
                    updates = {
                        'first_name': edit_first_name,
                        'last_name': edit_last_name,
                        'email': edit_email,
                        'phone': edit_phone,
                        'student_id': edit_roll_number,
                        'company': edit_company,
                        'current_position': edit_position,
                        'department': edit_department,
                        'year': str(edit_graduation_year),
                        'linkedin': edit_linkedin,
                        'skills': edit_skills,
                        'about': edit_about,
                        'is_verified': 1 if is_verified else 0
                    }
                    
                    if update_user_profile(alum['id'], **updates):
                        st.success("Alumni profile updated successfully!")
                        del st.session_state.edit_alumni_id
                        st.rerun()
                    else:
                        st.error("Failed to update alumni profile")
                
                if cancel:
                    del st.session_state.edit_alumni_id
                    st.rerun()
