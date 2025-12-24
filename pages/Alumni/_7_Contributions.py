import streamlit as st
from datetime import datetime
from utils.database import (
    add_contribution, get_contributions,
    get_user_by_id, get_alumni_profile
)

def alumni_contributions_page(user_id):
    """Alumni Contributions Page"""
    st.title("💡 Alumni Contributions")
    
    # Get alumni profile
    profile = get_alumni_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Make Contribution", "My Contributions", "Contribution Stats", "Impact"
    ])
    
    with tab1:
        # Make Contribution
        st.subheader("🎯 Make a Contribution")
        
        # Contribution type selection
        contribution_type = st.radio(
            "Select Contribution Type",
            ["Mentorship", "Job Posting", "Workshop/Seminar", "Donation", "Internship Opportunity", "Other"],
            horizontal=True
        )
        
        # Dynamic form based on contribution type
        if contribution_type == "Mentorship":
            with st.form("mentorship_form"):
                st.markdown("### 👨‍🏫 Mentorship Program")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Mentorship Title *", placeholder="e.g., Career Guidance for CS Students")
                    expertise_areas = st.multiselect(
                        "Areas of Expertise *",
                        ["Career Planning", "Technical Skills", "Interview Preparation", 
                         "Resume Review", "Higher Education", "Entrepreneurship", 
                         "Leadership", "Industry Insights", "Networking", "Other"]
                    )
                    availability = st.selectbox(
                        "Time Availability *",
                        ["1-2 hours/month", "3-5 hours/month", "5+ hours/month", "Flexible"]
                    )
                
                with col2:
                    target_students = st.multiselect(
                        "Target Student Groups",
                        ["All Students", "Freshmen", "Sophomores", "Juniors", 
                         "Seniors", "Graduating Students", "By Department"]
                    )
                    meeting_format = st.multiselect(
                        "Preferred Meeting Format",
                        ["One-on-One", "Group Sessions", "Virtual", "In-Person", "Hybrid"]
                    )
                    duration = st.selectbox(
                        "Mentorship Duration",
                        ["One-time", "1 month", "3 months", "6 months", "1 year", "Ongoing"]
                    )
                
                description = st.text_area(
                    "Mentorship Description *",
                    placeholder="Describe your mentoring approach, what students can expect, and how you can help...",
                    height=150
                )
                
                additional_info = st.text_area(
                    "Additional Information",
                    placeholder="Any specific requirements, expectations, or notes...",
                    height=100
                )
                
                submit = st.form_submit_button("Submit Mentorship Offer", type="primary")
                
                if submit:
                    if not all([title, expertise_areas, availability, description]):
                        st.error("Please fill all required fields (*)")
                    else:
                        contrib_data = {
                            'type': 'mentorship',
                            'title': title,
                            'description': f"{description}\n\nExpertise: {', '.join(expertise_areas)}\nAvailability: {availability}\nFormat: {', '.join(meeting_format)}\nDuration: {duration}\nTarget: {', '.join(target_students)}\n\n{additional_info}",
                            'hours': estimate_hours(availability),
                            'skills_required': ', '.join(expertise_areas)
                        }
                        
                        contribute(contrib_data, user_id, contribution_type)
        
        elif contribution_type == "Job Posting":
            with st.form("job_posting_form"):
                st.markdown("### 💼 Job Posting")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Job Title *", placeholder="e.g., Software Engineer Intern")
                    company = st.text_input("Company *", value=profile.get('company', ''))
                    job_type = st.selectbox(
                        "Job Type *",
                        ["Full Time", "Part Time", "Internship", "Contract", "Freelance"]
                    )
                    location = st.text_input("Location *", placeholder="e.g., Bangalore, India or Remote")
                
                with col2:
                    salary_range = st.text_input("Salary Range", placeholder="e.g., $60,000 - $80,000")
                    application_deadline = st.date_input("Application Deadline")
                    experience_level = st.selectbox(
                        "Experience Level",
                        ["Entry Level", "Junior", "Mid Level", "Senior", "Executive"]
                    )
                    remote_option = st.checkbox("Remote Work Available", value=False)
                
                description = st.text_area(
                    "Job Description *",
                    placeholder="Describe the role, responsibilities, and requirements...",
                    height=150
                )
                
                requirements = st.text_area(
                    "Requirements & Qualifications",
                    placeholder="List required skills, education, experience...",
                    height=100
                )
                
                benefits = st.text_area(
                    "Benefits & Perks",
                    placeholder="List company benefits, perks, culture...",
                    height=100
                )
                
                submit = st.form_submit_button("Post Job Opportunity", type="primary")
                
                if submit:
                    if not all([title, company, job_type, location, description]):
                        st.error("Please fill all required fields (*)")
                    else:
                        contrib_data = {
                            'type': 'job_posting',
                            'title': f"{title} at {company}",
                            'description': f"{description}\n\nJob Type: {job_type}\nLocation: {location}\nExperience Level: {experience_level}\nRemote: {'Yes' if remote_option else 'No'}\nSalary: {salary_range}\n\nRequirements:\n{requirements}\n\nBenefits:\n{benefits}",
                            'deadline': application_deadline.strftime('%Y-%m-%d')
                        }
                        
                        contribute(contrib_data, user_id, contribution_type)
        
        elif contribution_type == "Workshop/Seminar":
            with st.form("workshop_form"):
                st.markdown("### 🎓 Workshop/Seminar")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Workshop Title *", placeholder="e.g., AI in Modern Industry")
                    topic_area = st.selectbox(
                        "Topic Area *",
                        ["Technical Skills", "Career Development", "Industry Trends", 
                         "Soft Skills", "Entrepreneurship", "Research", "Other"]
                    )
                    duration = st.text_input("Duration *", placeholder="e.g., 2 hours, Half-day, Full-day")
                    format_type = st.selectbox(
                        "Format *",
                        ["Virtual", "In-Person", "Hybrid"]
                    )
                
                with col2:
                    target_audience = st.multiselect(
                        "Target Audience *",
                        ["All Students", "Specific Department", "Year-wise", 
                         "Skill Level", "Alumni", "Faculty"]
                    )
                    max_participants = st.number_input("Max Participants", min_value=1, value=30)
                    prerequisites = st.text_input("Prerequisites", placeholder="e.g., Basic Python knowledge")
                
                description = st.text_area(
                    "Workshop Description *",
                    placeholder="Describe what will be covered, learning outcomes, and agenda...",
                    height=150
                )
                
                materials = st.text_area(
                    "Materials/Resources Needed",
                    placeholder="List any materials participants should have...",
                    height=100
                )
                
                submit = st.form_submit_button("Submit Workshop Proposal", type="primary")
                
                if submit:
                    if not all([title, topic_area, duration, format_type, target_audience, description]):
                        st.error("Please fill all required fields (*)")
                    else:
                        contrib_data = {
                            'type': 'workshop',
                            'title': title,
                            'description': f"{description}\n\nTopic Area: {topic_area}\nDuration: {duration}\nFormat: {format_type}\nAudience: {', '.join(target_audience)}\nMax Participants: {max_participants}\nPrerequisites: {prerequisites}\n\nMaterials: {materials}",
                            'hours': estimate_workshop_hours(duration)
                        }
                        
                        contribute(contrib_data, user_id, contribution_type)
        
        elif contribution_type == "Donation":
            with st.form("donation_form"):
                st.markdown("### 💰 Donation")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    donation_type = st.selectbox(
                        "Donation Type *",
                        ["Scholarship Fund", "Department Fund", "Infrastructure", 
                         "Research Grant", "Event Sponsorship", "General Fund"]
                    )
                    amount = st.number_input("Amount ($) *", min_value=1, value=100)
                    frequency = st.selectbox(
                        "Frequency",
                        ["One-time", "Monthly", "Quarterly", "Yearly"]
                    )
                
                with col2:
                    anonymity = st.selectbox(
                        "Display Name As",
                        ["Full Name", "First Name Only", "Anonymous", "Company Name"]
                    )
                    receipt_needed = st.checkbox("Need Tax Receipt", value=True)
                    designation = st.text_input(
                        "Specific Designation",
                        placeholder="e.g., Computer Science Scholarship"
                    )
                
                message = st.text_area(
                    "Message (Optional)",
                    placeholder="Add a personal message or note...",
                    height=100
                )
                
                submit = st.form_submit_button("Make Donation", type="primary")
                
                if submit:
                    if not amount:
                        st.error("Please specify donation amount")
                    else:
                        display_name = ""
                        if anonymity == "Full Name":
                            display_name = f"{profile['first_name']} {profile['last_name']}"
                        elif anonymity == "First Name Only":
                            display_name = profile['first_name']
                        elif anonymity == "Company Name":
                            display_name = profile.get('company', 'Anonymous')
                        else:
                            display_name = "Anonymous Donor"
                        
                        contrib_data = {
                            'type': 'donation',
                            'title': f"{donation_type} Donation",
                            'description': f"Amount: ${amount}\nFrequency: {frequency}\nDesignation: {designation}\nDonor: {display_name}\n\nMessage: {message}",
                            'amount': amount
                        }
                        
                        contribute(contrib_data, user_id, contribution_type)
        
        else:  # Other contributions
            with st.form("other_contribution_form"):
                st.markdown("### 💡 Other Contribution")
                
                title = st.text_input("Contribution Title *", placeholder="e.g., Guest Lecture, Project Collaboration")
                contribution_category = st.selectbox(
                    "Category",
                    ["Guest Speaking", "Project Collaboration", "Research Partnership", 
                     "Curriculum Input", "Placement Support", "Alumni Engagement", "Other"]
                )
                
                description = st.text_area(
                    "Description *",
                    placeholder="Describe your contribution, how it will help, and any specifics...",
                    height=200
                )
                
                time_commitment = st.text_input("Time Commitment", placeholder="e.g., 5 hours per month")
                skills_involved = st.text_input("Skills/Expertise Involved", placeholder="e.g., Project Management, Technical Review")
                
                submit = st.form_submit_button("Submit Contribution", type="primary")
                
                if submit:
                    if not all([title, description]):
                        st.error("Please fill all required fields (*)")
                    else:
                        contrib_data = {
                            'type': 'other',
                            'title': title,
                            'description': f"Category: {contribution_category}\n\n{description}\n\nTime Commitment: {time_commitment}\nSkills: {skills_involved}"
                        }
                        
                        contribute(contrib_data, user_id, contribution_type)
    
    with tab2:
        # My Contributions
        st.subheader("📋 My Contributions")
        
        contributions = get_contributions(alumni_id=user_id)
        
        if contributions:
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                type_filter = st.selectbox(
                    "Filter by type",
                    ["All", "Mentorship", "Job Posting", "Workshop", "Donation", "Internship", "Other"]
                )
            
            with col_filter2:
                status_filter = st.selectbox(
                    "Filter by status",
                    ["All", "Pending", "Approved", "Completed", "Rejected"]
                )
            
            # Apply filters
            filtered_contributions = contributions
            
            if type_filter != "All":
                filtered_contributions = [c for c in filtered_contributions if c['type'] == type_filter.lower()]
            
            if status_filter != "All":
                filtered_contributions = [c for c in filtered_contributions if c['status'] == status_filter.lower()]
            
            # Display contributions
            if filtered_contributions:
                for contrib in filtered_contributions:
                    display_contribution_card(contrib, user_id)
            else:
                st.info(f"No {type_filter.lower()} contributions found with status '{status_filter.lower()}'.")
        else:
            st.info("You haven't made any contributions yet.")
            
            st.markdown("""
            ### Why contribute?
            
            **🎓 Give Back**  
            Support the next generation of MES students
            
            **🤝 Build Legacy**  
            Leave a lasting impact on your alma mater
            
            **💼 Professional Growth**  
            Develop leadership and mentoring skills
            
            **🔗 Strengthen Network**  
            Connect with students and fellow alumni
            
            **🏆 Recognition**  
            Get recognized for your contributions
            
            Ready to make your first contribution? Go to the "Make Contribution" tab!
            """)
    
    with tab3:
        # Contribution Stats
        st.subheader("📊 Contribution Statistics")
        
        contributions = get_contributions(alumni_id=user_id)
        
        if contributions:
            # Overall stats
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_contributions = len(contributions)
                st.metric("Total Contributions", total_contributions)
            
            with col_stat2:
                completed = len([c for c in contributions if c['status'] == 'completed'])
                st.metric("Completed", completed)
            
            with col_stat3:
                mentorship_count = len([c for c in contributions if c['type'] == 'mentorship'])
                st.metric("Mentorships", mentorship_count)
            
            with col_stat4:
                job_postings = len([c for c in contributions if c['type'] == 'job_posting'])
                st.metric("Jobs Posted", job_postings)
            
            # Contribution by type
            st.markdown("### 📈 Contribution Breakdown")
            
            import plotly.express as px
            import pandas as pd
            
            # Prepare data for chart
            type_counts = {}
            for contrib in contributions:
                contrib_type = contrib['type']
                type_counts[contrib_type] = type_counts.get(contrib_type, 0) + 1
            
            if type_counts:
                df = pd.DataFrame({
                    'Type': [t.replace('_', ' ').title() for t in type_counts.keys()],
                    'Count': list(type_counts.values())
                })
                
                fig = px.pie(df, values='Count', names='Type', 
                           title="Contributions by Type")
                st.plotly_chart(fig, use_container_width=True)
            
            # Status distribution
            st.markdown("### 🎯 Contribution Status")
            
            status_counts = {}
            for contrib in contributions:
                status = contrib['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                df_status = pd.DataFrame({
                    'Status': [s.title() for s in status_counts.keys()],
                    'Count': list(status_counts.values())
                })
                
                fig_status = px.bar(df_status, x='Status', y='Count',
                                  title="Contributions by Status",
                                  color='Status')
                st.plotly_chart(fig_status, use_container_width=True)
            
            # Recent activity
            st.markdown("### 🕒 Recent Activity")
            
            recent_contributions = sorted(contributions, key=lambda x: x['created_at'], reverse=True)[:5]
            
            for contrib in recent_contributions:
                col_recent1, col_recent2 = st.columns([3, 1])
                with col_recent1:
                    type_icons = {
                        'mentorship': '👨‍🏫',
                        'job_posting': '💼',
                        'workshop': '🎓',
                        'donation': '💰',
                        'internship': '🎯',
                        'other': '💡'
                    }
                    icon = type_icons.get(contrib['type'], '💡')
                    st.markdown(f"{icon} **{contrib['title']}**")
                    st.caption(f"Status: {contrib['status'].title()} • {contrib['created_at'][:10]}")
                with col_recent2:
                    if st.button("View", key=f"view_stat_{contrib['id']}"):
                        display_contribution_details(contrib)
                st.markdown("---")
        else:
            st.info("No contribution statistics available yet.")
    
    with tab4:
        # Impact
        st.subheader("🌟 Your Impact")
        
        contributions = get_contributions(alumni_id=user_id)
        completed_contributions = [c for c in contributions if c['status'] == 'completed']
        
        if completed_contributions:
            # Impact metrics
            col_impact1, col_impact2, col_impact3 = st.columns(3)
            
            with col_impact1:
                # Estimate students helped
                students_helped = 0
                for contrib in completed_contributions:
                    if contrib['type'] == 'mentorship':
                        students_helped += 5  # Estimated
                    elif contrib['type'] == 'workshop':
                        students_helped += 20  # Estimated
                st.metric("Students Helped", students_helped)
            
            with col_impact2:
                # Jobs/internships provided
                opportunities = len([c for c in completed_contributions if c['type'] in ['job_posting', 'internship']])
                st.metric("Opportunities Provided", opportunities)
            
            with col_impact3:
                # Total hours contributed
                total_hours = sum(c.get('hours', 0) for c in completed_contributions)
                st.metric("Hours Contributed", total_hours)
            
            # Success stories
            st.markdown("### 🎉 Success Stories")
            
            # This would ideally come from student feedback
            st.info("Success stories from your contributions will appear here as students provide feedback.")
            
            # Impact visualization
            st.markdown("### 📊 Impact Timeline")
            
            # Create a timeline of contributions
            timeline_data = []
            for contrib in completed_contributions:
                timeline_data.append({
                    'Date': contrib['created_at'][:10],
                    'Type': contrib['type'].replace('_', ' ').title(),
                    'Title': contrib['title']
                })
            
            if timeline_data:
                import plotly.express as px
                
                df_timeline = pd.DataFrame(timeline_data)
                df_timeline['Date'] = pd.to_datetime(df_timeline['Date'])
                df_timeline = df_timeline.sort_values('Date')
                
                fig_timeline = px.scatter(df_timeline, x='Date', y='Type',
                                        size=[10]*len(df_timeline),
                                        hover_name='Title',
                                        title="Your Contribution Timeline")
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Recognition
            st.markdown("### 🏆 Recognition")
            
            if len(completed_contributions) >= 5:
                st.success("🎖️ **Gold Contributor** - Thank you for your outstanding contributions!")
            elif len(completed_contributions) >= 3:
                st.info("🥈 **Silver Contributor** - Your contributions are making a difference!")
            elif len(completed_contributions) >= 1:
                st.info("🥉 **Bronze Contributor** - Thank you for giving back!")
            
            # Share impact
            st.markdown("### 📣 Share Your Impact")
            
            col_share1, col_share2 = st.columns(2)
            
            with col_share1:
                if st.button("Share on LinkedIn", use_container_width=True):
                    st.info("LinkedIn sharing coming soon!")
            
            with col_share2:
                if st.button("Generate Impact Report", use_container_width=True):
                    st.info("Report generation coming soon!")
        else:
            st.info("Complete your first contribution to see your impact here!")
            
            st.markdown("""
            ### 🌟 The Impact You Can Make
            
            **👨‍🎓 For Students:**
            - Provide career guidance and mentorship
            - Offer internship and job opportunities
            - Share industry knowledge and skills
            - Inspire the next generation
            
            **🏫 For MES:**
            - Strengthen the alumni network
            - Enhance educational programs
            - Support campus development
            - Build a stronger community
            
            **👤 For You:**
            - Professional fulfillment
            - Network expansion
            - Skill development
            - Legacy building
            
            **Ready to make an impact?** Start with your first contribution!
            """)

def estimate_hours(availability):
    """Estimate hours from availability string"""
    if "1-2 hours/month" in availability:
        return 1.5
    elif "3-5 hours/month" in availability:
        return 4
    elif "5+ hours/month" in availability:
        return 6
    else:
        return 3

def estimate_workshop_hours(duration):
    """Estimate hours from workshop duration"""
    if "hour" in duration.lower():
        try:
            return int(duration.split()[0])
        except:
            return 2
    elif "half" in duration.lower():
        return 4
    elif "full" in duration.lower():
        return 8
    else:
        return 2

def contribute(contrib_data, user_id, contrib_type):
    """Process contribution submission"""
    contribution_id = add_contribution(
        alumni_id=user_id,
        type=contrib_data['type'],
        title=contrib_data['title'],
        description=contrib_data['description'],
        amount=contrib_data.get('amount'),
        hours=contrib_data.get('hours'),
        skills_required=contrib_data.get('skills_required'),
        deadline=contrib_data.get('deadline')
    )
    
    if contribution_id:
        st.success(f"🎉 {contrib_type} contribution submitted successfully!")
        st.balloons()
        
        st.markdown(f"""
        ### What happens next?
        
        1. **Review Process** - Your contribution will be reviewed by the platform team
        2. **Approval** - If approved, it will be made available to students
        3. **Matching** - Students will be matched based on their interests
        4. **Implementation** - You'll be connected with interested students
        5. **Completion** - After successful completion, you'll receive recognition
        
        **Status:** Pending Review
        **Reference ID:** `{contribution_id}`
        
        You can track the status in "My Contributions" tab.
        """)
        
        if st.button("View My Contributions"):
            st.session_state.current_page = "Alumni/Contributions"
            st.rerun()
    else:
        st.error("Failed to submit contribution")

def display_contribution_card(contribution, user_id):
    """Display a contribution card"""
    with st.container():
        st.markdown(f"<div style='background: white; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #8B5CF6;'>", unsafe_allow_html=True)
        
        # Header
        col_head1, col_head2 = st.columns([4, 1])
        
        with col_head1:
            type_icons = {
                'mentorship': '👨‍🏫',
                'job_posting': '💼',
                'workshop': '🎓',
                'donation': '💰',
                'internship': '🎯',
                'other': '💡'
            }
            icon = type_icons.get(contribution['type'], '💡')
            st.markdown(f"{icon} **{contribution['title']}**")
            
            # Type and status
            type_display = contribution['type'].replace('_', ' ').title()
            status_colors = {
                'pending': '🟡',
                'approved': '🟢',
                'completed': '✅',
                'rejected': '🔴'
            }
            status_icon = status_colors.get(contribution['status'], '⚪')
            st.caption(f"{type_display} • {status_icon} {contribution['status'].title()}")
        
        with col_head2:
            # Date
            st.caption(f"📅 {contribution['created_at'][:10]}")
            
            # Amount or hours if applicable
            if contribution.get('amount'):
                st.caption(f"💰 ${contribution['amount']}")
            elif contribution.get('hours'):
                st.caption(f"⏱️ {contribution['hours']} hours")
        
        # Description preview
        if contribution.get('description'):
            # Get first paragraph for preview
            desc_lines = contribution['description'].split('\n')
            preview = desc_lines[0][:150] + "..." if len(desc_lines[0]) > 150 else desc_lines[0]
            st.markdown(f"> {preview}")
        
        # Action buttons
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            if st.button("View Details", key=f"details_{contribution['id']}"):
                display_contribution_details(contribution)
        
        with col_act2:
            if contribution['status'] == 'pending':
                if st.button("Edit", key=f"edit_{contribution['id']}"):
                    st.info("Edit feature coming soon!")
            elif contribution['status'] == 'approved':
                if st.button("Manage", key=f"manage_{contribution['id']}"):
                    st.info("Management dashboard coming soon!")
        
        with col_act3:
            if st.button("Delete", key=f"delete_{contribution['id']}"):
                st.warning("Are you sure you want to delete this contribution?")
                if st.button("Confirm Delete", key=f"confirm_del_{contribution['id']}"):
                    st.info("Delete feature coming soon!")
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_contribution_details(contribution):
    """Display detailed view of a contribution"""
    with st.expander("Contribution Details", expanded=True):
        st.markdown(f"### {contribution['title']}")
        
        # Basic info
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.markdown(f"**Type:** {contribution['type'].replace('_', ' ').title()}")
            st.markdown(f"**Status:** {contribution['status'].title()}")
            st.markdown(f"**Submitted:** {contribution['created_at'][:10]}")
        
        with col_info2:
            if contribution.get('deadline'):
                st.markdown(f"**Deadline:** {contribution['deadline']}")
            if contribution.get('hours'):
                st.markdown(f"**Time Commitment:** {contribution['hours']} hours")
            if contribution.get('amount'):
                st.markdown(f"**Amount:** ${contribution['amount']}")
        
        # Full description
        st.markdown("### 📝 Description")
        st.markdown(contribution['description'])
        
        # Status-specific actions
        if contribution['status'] == 'pending':
            st.info("⏳ Your contribution is under review. You'll be notified once it's approved.")
        elif contribution['status'] == 'approved':
            st.success("✅ Your contribution is approved and visible to students!")
            
            # Show engagement metrics (would come from database)
            col_eng1, col_eng2, col_eng3 = st.columns(3)
            with col_eng1:
                st.metric("Views", "0")
            with col_eng2:
                st.metric("Interested", "0")
            with col_eng3:
                st.metric("Matches", "0")
        
        elif contribution['status'] == 'completed':
            st.success("🎉 Contribution successfully completed!")
            
            # Feedback section
            st.markdown("### 💬 Feedback")
            st.info("Student feedback will appear here once available.")
        
        elif contribution['status'] == 'rejected':
            st.error("❌ Contribution was not approved.")
            st.info("Please review the contribution guidelines and resubmit if appropriate.")
