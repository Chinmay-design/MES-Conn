import streamlit as st
from datetime import datetime
from utils.database import (
    get_job_postings, add_job_posting,
    get_user_by_id, get_alumni_profile
)

def alumni_jobs_page(user_id):
    """Alumni Jobs Page"""
    st.title("💼 Job Postings")
    
    # Get alumni profile
    profile = get_alumni_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "Post Job", "My Job Postings", "Job Analytics"
    ])
    
    with tab1:
        # Post Job
        st.subheader("📝 Post a Job Opportunity")
        
        with st.form("post_job_form"):
            # Job details
            st.markdown("### 🏢 Job Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                position = st.text_input("Job Title *", placeholder="e.g., Software Engineer")
                company = st.text_input("Company *", value=profile.get('company', ''))
                job_type = st.selectbox(
                    "Job Type *",
                    ["Full Time", "Part Time", "Internship", "Contract", "Freelance"]
                )
                location = st.text_input("Location *", placeholder="e.g., Bangalore or Remote")
            
            with col2:
                salary_range = st.text_input("Salary Range", placeholder="e.g., ₹8,00,000 - ₹12,00,000")
                experience_level = st.selectbox(
                    "Experience Level",
                    ["Entry Level", "Junior (0-2 years)", "Mid Level (2-5 years)", 
                     "Senior (5+ years)", "Executive", "All Levels"]
                )
                application_deadline = st.date_input("Application Deadline")
                remote_option = st.checkbox("Remote Work Available", value=False)
            
            # Job description
            st.markdown("### 📝 Job Description")
            
            description = st.text_area(
                "Job Description *",
                placeholder="Describe the role, responsibilities, team, and projects...",
                height=150
            )
            
            # Requirements and qualifications
            st.markdown("### 🎯 Requirements & Qualifications")
            
            requirements = st.text_area(
                "Required Skills & Qualifications",
                placeholder="List required education, skills, experience, certifications...",
                height=100
            )
            
            preferred_qualifications = st.text_area(
                "Preferred Qualifications",
                placeholder="List preferred skills or experience (optional)...",
                height=80
            )
            
            # Benefits and culture
            st.markdown("### 🌟 Benefits & Culture")
            
            benefits = st.text_area(
                "Benefits & Perks",
                placeholder="List compensation, benefits, work culture, growth opportunities...",
                height=100
            )
            
            # Application process
            st.markdown("### 📨 Application Process")
            
            col_app1, col_app2 = st.columns(2)
            
            with col_app1:
                application_method = st.radio(
                    "Application Method",
                    ["Apply on Company Website", "Email Resume", "Platform Application", "Other"]
                )
            
            with col_app2:
                if application_method == "Apply on Company Website":
                    application_link = st.text_input("Application URL", placeholder="https://company.com/careers/...")
                elif application_method == "Email Resume":
                    application_email = st.text_input("Application Email", placeholder="careers@company.com")
                else:
                    application_instructions = st.text_input("Application Instructions")
            
            # Target students
            st.markdown("### 🎓 Target Students")
            
            target_departments = st.multiselect(
                "Preferred Departments",
                ["Computer Science", "Electronics & Communication", "Mechanical", 
                 "Civil", "Electrical", "Information Technology", "Chemical", 
                 "Biotechnology", "Aerospace", "All Departments"]
            )
            
            target_years = st.multiselect(
                "Target Academic Years",
                ["Final Year", "Pre-Final Year", "All Years"]
            )
            
            # Contact information
            st.markdown("### 📞 Contact Information")
            
            col_contact1, col_contact2 = st.columns(2)
            
            with col_contact1:
                contact_name = st.text_input("Contact Person", value=f"{profile['first_name']} {profile['last_name']}")
                contact_email = st.text_input("Contact Email", value=profile['email'])
            
            with col_contact2:
                contact_phone = st.text_input("Contact Phone", value=profile.get('phone', ''))
                linkedin_profile = st.text_input("LinkedIn Profile", value=profile.get('linkedin', ''))
            
            # Submit button
            submit = st.form_submit_button("Post Job Opportunity", type="primary")
            
            if submit:
                if not all([position, company, job_type, location, description]):
                    st.error("Please fill all required fields (*)")
                else:
                    # Prepare job data
                    job_type_db = job_type.lower().replace(' ', '_')
                    
                    # Build description with all details
                    full_description = f"{description}\n\n"
                    full_description += f"**Job Type:** {job_type}\n"
                    full_description += f"**Experience Level:** {experience_level}\n"
                    full_description += f"**Location:** {location}\n"
                    full_description += f"**Remote Option:** {'Yes' if remote_option else 'No'}\n"
                    full_description += f"**Salary Range:** {salary_range}\n\n"
                    
                    full_description += f"**Requirements:**\n{requirements}\n\n"
                    if preferred_qualifications:
                        full_description += f"**Preferred Qualifications:**\n{preferred_qualifications}\n\n"
                    
                    full_description += f"**Benefits:**\n{benefits}\n\n"
                    
                    full_description += f"**Application Method:** {application_method}\n"
                    if application_method == "Apply on Company Website" and application_link:
                        full_description += f"**Application Link:** {application_link}\n"
                    elif application_method == "Email Resume" and application_email:
                        full_description += f"**Application Email:** {application_email}\n"
                    elif application_instructions:
                        full_description += f"**Instructions:** {application_instructions}\n"
                    
                    full_description += f"\n**Target Departments:** {', '.join(target_departments)}\n"
                    full_description += f"**Target Years:** {', '.join(target_years)}\n\n"
                    
                    full_description += f"**Contact Information:**\n"
                    full_description += f"- Name: {contact_name}\n"
                    full_description += f"- Email: {contact_email}\n"
                    if contact_phone:
                        full_description += f"- Phone: {contact_phone}\n"
                    if linkedin_profile:
                        full_description += f"- LinkedIn: {linkedin_profile}\n"
                    
                    # Prepare job posting data
                    job_data = {
                        'company': company,
                        'position': position,
                        'description': full_description,
                        'requirements': requirements,
                        'location': location,
                        'salary_range': salary_range,
                        'job_type': job_type_db,
                        'application_link': application_link if application_method == "Apply on Company Website" else None,
                        'deadline': application_deadline.strftime('%Y-%m-%d')
                    }
                    
                    # Add job posting
                    job_id = add_job_posting(
                        posted_by=user_id,
                        **job_data
                    )
                    
                    if job_id:
                        st.success(f"🎉 Job posting for '{position}' created successfully!")
                        st.balloons()
                        
                        with st.expander("Next Steps", expanded=True):
                            st.markdown(f"""
                            ### 🚀 Your job posting is live!
                            
                            **Job ID:** `{job_id}`
                            **Share Link:** `mes-connect.com/jobs/{job_id}`
                            
                            **What happens next:**
                            
                            1. **📢 Promotion** - The job will be promoted to relevant students
                            2. **👥 Student Applications** - Students will start applying
                            3. **📨 Notifications** - You'll receive application notifications
                            4. **🤝 Candidate Review** - Review applications through the platform
                            5. **📞 Interview Process** - Coordinate interviews with candidates
                            
                            **Best Practices:**
                            - Respond to applicants promptly
                            - Provide clear next steps
                            - Give constructive feedback when possible
                            - Keep the job posting updated
                            
                            **Quick Actions:**
                            """)
                            
                            col_action1, col_action2, col_action3 = st.columns(3)
                            with col_action1:
                                if st.button("View Job Posting", type="primary"):
                                    st.rerun()
                            with col_action2:
                                if st.button("Share on LinkedIn"):
                                    st.info("LinkedIn sharing coming soon!")
                            with col_action3:
                                if st.button("Track Applications"):
                                    st.session_state.current_page = "Alumni/Jobs"
                                    st.rerun()
                    else:
                        st.error("Failed to post job")
    
    with tab2:
        # My Job Postings
        st.subheader("📋 My Job Postings")
        
        # Get job postings
        all_jobs = get_job_postings(active_only=False, limit=100)
        my_jobs = [j for j in all_jobs if j['posted_by'] == user_id]
        
        if my_jobs:
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                status_filter = st.selectbox(
                    "Filter by status",
                    ["All", "Active", "Expired", "Closed"]
                )
            
            with col_filter2:
                job_type_filter = st.selectbox(
                    "Filter by job type",
                    ["All", "Full Time", "Part Time", "Internship", "Contract", "Freelance"]
                )
            
            # Apply filters
            filtered_jobs = my_jobs
            
            if status_filter == "Active":
                filtered_jobs = [j for j in filtered_jobs if j['is_active'] == 1 and 
                               (not j.get('deadline') or j['deadline'] >= datetime.now().strftime('%Y-%m-%d'))]
            elif status_filter == "Expired":
                filtered_jobs = [j for j in filtered_jobs if j.get('deadline') and j['deadline'] < datetime.now().strftime('%Y-%m-%d')]
            elif status_filter == "Closed":
                filtered_jobs = [j for j in filtered_jobs if j['is_active'] == 0]
            
            if job_type_filter != "All":
                job_type_db = job_type_filter.lower().replace(' ', '_')
                filtered_jobs = [j for j in filtered_jobs if j.get('job_type') == job_type_db]
            
            # Display job postings
            if filtered_jobs:
                st.markdown(f"Found **{len(filtered_jobs)}** job postings")
                
                for job in filtered_jobs:
                    display_alumni_job_card(job, user_id)
            else:
                st.info(f"No {status_filter.lower()} job postings found.")
        else:
            st.info("You haven't posted any jobs yet.")
            
            st.markdown("""
            ### 💼 Why post jobs on MES-Connect?
            
            **🎯 Targeted Audience**  
            Reach qualified MES students and alumni
            
            **🤝 Trusted Network**  
            Connect with candidates from your alma mater
            
            **💰 Cost Effective**  
            Free job postings for alumni
            
            **⚡ Quick Hiring**  
            Faster recruitment through alumni referrals
            
            **🌟 Quality Candidates**  
            Access to top talent from MES
            
            **Ready to post your first job?** Go to the "Post Job" tab!
            """)
    
    with tab3:
        # Job Analytics
        st.subheader("📊 Job Posting Analytics")
        
        my_jobs = [j for j in get_job_postings(active_only=False, limit=100) if j['posted_by'] == user_id]
        
        if my_jobs:
            # Overall stats
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_jobs = len(my_jobs)
                st.metric("Total Jobs Posted", total_jobs)
            
            with col_stat2:
                active_jobs = len([j for j in my_jobs if j['is_active'] == 1])
                st.metric("Active Jobs", active_jobs)
            
            with col_stat3:
                # This would come from applications database
                total_applications = 0
                st.metric("Total Applications", total_applications)
            
            with col_stat4:
                # This would come from applications database
                interview_rate = "0%"
                st.metric("Interview Rate", interview_rate)
            
            # Job type distribution
            st.markdown("### 📈 Job Type Distribution")
            
            import plotly.express as px
            import pandas as pd
            
            job_type_counts = {}
            for job in my_jobs:
                job_type = job.get('job_type', 'full_time')
                job_type_display = job_type.replace('_', ' ').title()
                job_type_counts[job_type_display] = job_type_counts.get(job_type_display, 0) + 1
            
            if job_type_counts:
                df = pd.DataFrame({
                    'Job Type': list(job_type_counts.keys()),
                    'Count': list(job_type_counts.values())
                })
                
                fig = px.pie(df, values='Count', names='Job Type',
                           title="Jobs by Type")
                st.plotly_chart(fig, use_container_width=True)
            
            # Application trends
            st.markdown("### 📅 Application Trends")
            
            # This would show application timeline
            st.info("Application analytics dashboard coming soon!")
            
            # Performance metrics
            st.markdown("### 🎯 Performance Metrics")
            
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            
            with col_metric1:
                st.metric("Average Applications/Job", "0")
            
            with col_metric2:
                st.metric("Response Time", "0 days")
            
            with col_metric3:
                st.metric("Hire Rate", "0%")
            
            # Recommendations
            st.markdown("### 💡 Recommendations")
            
            with st.expander("Improve Your Job Postings"):
                st.markdown("""
                **Based on your job posting analytics:**
                
                1. **📝 Improve Descriptions** - Make job descriptions more detailed
                2. **💰 Competitive Salaries** - Include salary ranges for better response
                3. **🏢 Company Branding** - Add company culture and benefits
                4. **📞 Clear Contact Info** - Make it easy for candidates to reach out
                5. **🎯 Targeted Posting** - Specify departments and years for better matches
                6. **⚡ Quick Responses** - Respond to applications within 48 hours
                7. **🔄 Regular Updates** - Keep job postings updated and active
                """)
        else:
            st.info("Post your first job to see analytics here!")

def display_alumni_job_card(job, user_id):
    """Display an alumni job card"""
    with st.container():
        # Determine status
        is_active = job['is_active'] == 1
        has_deadline = job.get('deadline')
        is_expired = has_deadline and job['deadline'] < datetime.now().strftime('%Y-%m-%d')
        
        status_color = "🟢" if is_active and not is_expired else "🔴"
        status_text = "Active" if is_active and not is_expired else "Expired/Closed"
        
        # Job header
        col_header1, col_header2 = st.columns([4, 1])
        
        with col_header1:
            st.markdown(f"### {job['position']}")
            st.markdown(f"#### 🏢 {job['company']}")
            
            # Status
            st.caption(f"{status_color} {status_text}")
            
            if is_expired:
                st.caption(f"📅 Deadline: {job['deadline']} (Expired)")
            elif has_deadline:
                st.caption(f"📅 Deadline: {job['deadline']}")
        
        with col_header2:
            # Job type
            job_type_display = job.get('job_type', 'full_time').replace('_', ' ').title()
            st.markdown(f"**{job_type_display}**")
            
            # Location
            if job.get('location'):
                st.caption(f"📍 {job['location']}")
        
        # Job details
        col_details1, col_details2 = st.columns(2)
        
        with col_details1:
            if job.get('salary_range'):
                st.markdown(f"💰 **Salary:** {job['salary_range']}")
            
            if job.get('experience_level'):
                st.caption(f"🎯 {job.get('experience_level')}")
        
        with col_details2:
            # Application stats (would come from database)
            applications = 0  # Placeholder
            st.markdown(f"📨 **Applications:** {applications}")
            
            st.caption(f"Posted: {job['created_at'][:10]}")
        
        # Description preview
        if job.get('description'):
            # Extract first part for preview
            desc_lines = job['description'].split('\n')
            preview = desc_lines[0][:200] + "..." if len(desc_lines[0]) > 200 else desc_lines[0]
            st.markdown(f"> {preview}")
        
        # Action buttons
        col_actions1, col_actions2, col_actions3 = st.columns(3)
        
        with col_actions1:
            if st.button("View Details", key=f"view_job_{job['id']}"):
                display_job_details(job, user_id)
        
        with col_actions2:
            if is_active and not is_expired:
                if st.button("Edit", key=f"edit_job_{job['id']}"):
                    st.info("Edit job feature coming soon!")
            else:
                if st.button("Repost", key=f"repost_{job['id']}"):
                    st.info("Repost feature coming soon!")
        
        with col_actions3:
            if st.button("Manage Applications", key=f"manage_app_{job['id']}"):
                st.info("Application management coming soon!")
        
        st.markdown("---")

def display_job_details(job, user_id):
    """Display detailed view of a job"""
    with st.expander("Job Details", expanded=True):
        # Basic info
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown(f"**Position:** {job['position']}")
            st.markdown(f"**Company:** {job['company']}")
            st.markdown(f"**Job Type:** {job.get('job_type', 'full_time').replace('_', ' ').title()}")
            st.markdown(f"**Location:** {job.get('location', 'Not specified')}")
        
        with col_info2:
            st.markdown(f"**Posted:** {job['created_at'][:10]}")
            if job.get('deadline'):
                st.markdown(f"**Deadline:** {job['deadline']}")
            if job.get('salary_range'):
                st.markdown(f"**Salary Range:** {job['salary_range']}")
            st.markdown(f"**Status:** {'Active' if job['is_active'] == 1 else 'Closed'}")
        
        # Full description
        st.markdown("### 📝 Job Description")
        st.markdown(job['description'])
        
        # Posted by info
        st.markdown("### 📞 Contact Information")
        st.markdown(f"**Posted by:** {job['first_name']} {job['last_name']}")
        if job.get('poster_company'):
            st.markdown(f"**Company:** {job['poster_company']}")
        
        # Management actions
        st.markdown("### 🛠️ Job Management")
        
        col_manage1, col_manage2, col_manage3 = st.columns(3)
        
        with col_manage1:
            if st.button("View Applications", key=f"view_apps_{job['id']}"):
                st.info("Application viewer coming soon!")
        
        with col_manage2:
            if job['is_active'] == 1:
                if st.button("Close Job", key=f"close_{job['id']}"):
                    st.warning("Close this job posting?")
                    if st.button("Confirm Close", key=f"confirm_close_{job['id']}"):
                        st.info("Close job feature coming soon!")
            else:
                if st.button("Reactivate", key=f"reactivate_{job['id']}"):
                    st.info("Reactivate feature coming soon!")
        
        with col_manage3:
            if st.button("Share Job", key=f"share_job_{job['id']}"):
                st.info("Share job feature coming soon!")
        
        # Analytics
        st.markdown("### 📊 Job Analytics")
        
        col_analytics1, col_analytics2, col_analytics3 = st.columns(3)
        
        with col_analytics1:
            st.metric("Total Views", "0")
        
        with col_analytics2:
            st.metric("Applications", "0")
        
        with col_analytics3:
            st.metric("Shortlisted", "0")
