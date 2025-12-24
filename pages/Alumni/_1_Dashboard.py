import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from utils.database import (
    get_alumni_profile, get_events, get_announcements,
    get_friends, get_all_users, get_job_postings,
    get_contributions, get_user_by_id
)

def alumni_dashboard_page(user_id):
    """Alumni Dashboard"""
    st.title("👨‍🎓 Alumni Dashboard")
    
    # Get user profile
    profile = get_alumni_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Welcome section with quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Connections", len(get_friends(user_id)))
    
    with col2:
        contributions = get_contributions(alumni_id=user_id)
        st.metric("Contributions", len(contributions))
    
    with col3:
        job_postings = get_job_postings(active_only=True, limit=100)
        user_jobs = [j for j in job_postings if j['posted_by'] == user_id]
        st.metric("Jobs Posted", len(user_jobs))
    
    with col4:
        from utils.database import get_notifications
        notifications = get_notifications(user_id, unread_only=True)
        st.metric("Notifications", len(notifications))
    
    st.markdown("---")
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Announcements
        st.subheader("📢 Alumni Announcements")
        announcements = get_announcements(target_role='alumni', limit=5)
        
        if announcements:
            for ann in announcements:
                with st.container():
                    col_a1, col_a2 = st.columns([4, 1])
                    with col_a1:
                        st.markdown(f"**{ann['title']}**")
                        st.caption(f"By {ann['first_name']} {ann['last_name']} • {ann['created_at'][:10]}")
                    with col_a2:
                        priority_color = {
                            'urgent': '🔴',
                            'high': '🟠',
                            'normal': '🔵',
                            'low': '⚪'
                        }.get(ann['priority'], '⚪')
                        st.markdown(f"**{priority_color} {ann['priority'].upper()}**")
                    
                    st.markdown(f"{ann['content'][:200]}...")
                    if len(ann['content']) > 200:
                        with st.expander("Read more"):
                            st.markdown(ann['content'])
                    st.markdown("---")
        else:
            st.info("No announcements yet.")
        
        # Upcoming Events
        st.subheader("📅 Alumni Events")
        events = get_events(upcoming=True, limit=3, user_id=user_id)
        
        if events:
            for event in events:
                with st.container():
                    col_e1, col_e2 = st.columns([3, 1])
                    with col_e1:
                        st.markdown(f"**{event['title']}**")
                        st.caption(f"📅 {event['event_date']} 🕒 {event['event_time'] or 'TBA'}")
                        if event['location']:
                            st.caption(f"📍 {event['location']}")
                        st.caption(f"👥 {event['participant_count']} participants • Organized by {event['organizer_first_name']}")
                    with col_e2:
                        if event.get('is_registered'):
                            st.success("✅ Registered")
                        else:
                            if st.button("Register", key=f"alum_reg_{event['id']}"):
                                from utils.database import register_for_event
                                success, msg = register_for_event(event['id'], user_id)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    st.markdown("---")
        else:
            st.info("No upcoming alumni events.")
    
    with col2:
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        quick_actions = [
            ("🤝 Network", "Alumni/Networking"),
            ("💼 Post Job", "Alumni/Jobs"),
            ("💡 Contribute", "Alumni/Contributions"),
            ("👥 Mentor", "Alumni/Networking"),
            ("📅 Create Event", "Alumni/Events"),
            ("📊 Analytics", "#"),
            ("⚙️ Settings", "Alumni/Settings")
        ]
        
        for action_text, action_page in quick_actions:
            if st.button(action_text, use_container_width=True, key=f"alum_quick_{action_text}"):
                if action_page.startswith("#"):
                    st.info(f"{action_text} feature coming soon!")
                else:
                    st.session_state.current_page = action_page
                    st.rerun()
        
        # Recent Connections
        st.subheader("🤝 Recent Connections")
        connections = get_friends(user_id)[:5]
        
        if connections:
            for conn in connections:
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"**{conn['first_name']} {conn['last_name']}**")
                    st.caption(f"{conn.get('current_position', '')}")
                with col_c2:
                    if st.button("💬", key=f"alum_chat_{conn['id']}"):
                        st.session_state.chat_with = conn['id']
                        st.session_state.current_page = "Alumni/Chat"
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No connections yet. Start networking!")
        
        # Alumni Stats
        st.subheader("📊 Alumni Network")
        
        all_alumni = get_all_users(role='alumni')
        alumni_by_company = {}
        
        for alum in all_alumni:
            if alum.get('company'):
                company = alum['company']
                alumni_by_company[company] = alumni_by_company.get(company, 0) + 1
        
        # Show top companies
        if alumni_by_company:
            top_companies = sorted(alumni_by_company.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for company, count in top_companies:
                st.markdown(f"**{company}:** {count} alumni")
        else:
            st.info("Network statistics loading...")
    
    # Job Postings Section
    st.markdown("---")
    st.subheader("💼 Your Job Postings")
    
    job_postings = get_job_postings(active_only=True, limit=100)
    my_jobs = [j for j in job_postings if j['posted_by'] == user_id]
    
    if my_jobs:
        for job in my_jobs[:3]:  # Show first 3
            with st.container():
                col_j1, col_j2, col_j3 = st.columns([3, 1, 1])
                with col_j1:
                    st.markdown(f"**{job['position']} at {job['company']}**")
                    st.caption(f"📍 {job['location'] or 'Remote'} • 📅 Posted: {job['created_at'][:10]}")
                with col_j2:
                    applications = 0  # Would need to get from database
                    st.metric("Applications", applications)
                with col_j3:
                    if st.button("Manage", key=f"manage_job_{job['id']}"):
                        st.session_state.current_page = "Alumni/Jobs"
                        st.rerun()
                st.markdown("---")
    else:
        st.info("You haven't posted any jobs yet.")
        
        if st.button("Post Your First Job", type="primary"):
            st.session_state.current_page = "Alumni/Jobs"
            st.rerun()
    
    # Contributions Section
    st.markdown("---")
    st.subheader("💡 Your Contributions")
    
    contributions = get_contributions(alumni_id=user_id)
    
    if contributions:
        # Group by type
        contributions_by_type = {}
        for contrib in contributions:
            contrib_type = contrib['type']
            contributions_by_type[contrib_type] = contributions_by_type.get(contrib_type, 0) + 1
        
        # Display contribution types
        col_cont1, col_cont2, col_cont3 = st.columns(3)
        
        contrib_types = list(contributions_by_type.keys())[:3]
        for i, contrib_type in enumerate(contrib_types):
            with [col_cont1, col_cont2, col_cont3][i]:
                count = contributions_by_type[contrib_type]
                type_icons = {
                    'mentorship': '👨‍🏫',
                    'donation': '💰',
                    'workshop': '🎓',
                    'job_posting': '💼',
                    'internship': '🎯',
                    'other': '💡'
                }
                icon = type_icons.get(contrib_type, '💡')
                st.metric(f"{icon} {contrib_type.title()}", count)
        
        # Show recent contributions
        with st.expander("View Recent Contributions"):
            for contrib in contributions[:5]:
                st.markdown(f"• **{contrib['title']}** - {contrib['status'].title()}")
    else:
        st.info("You haven't made any contributions yet.")
        
        col_contrib1, col_contrib2 = st.columns(2)
        with col_contrib1:
            if st.button("Start Mentoring", type="primary"):
                st.session_state.current_page = "Alumni/Contributions"
                st.rerun()
        with col_contrib2:
            if st.button("Post Workshop", type="secondary"):
                st.session_state.current_page = "Alumni/Contributions"
                st.rerun()
    
    # Network Suggestions
    st.markdown("---")
    st.subheader("👥 Suggested Connections")
    
    all_users = get_all_users(exclude_id=user_id)
    connections = get_friends(user_id)
    connection_ids = [c['id'] for c in connections]
    
    # Filter out existing connections
    potential_connections = [u for u in all_users if u['id'] not in connection_ids]
    
    # Prioritize alumni from same company/department
    suggestions = []
    for user in potential_connections:
        score = 0
        if user['role'] == 'alumni':
            score += 2
        if user.get('company') == profile.get('company'):
            score += 3
        if user.get('department') == profile.get('department'):
            score += 2
        suggestions.append((score, user))
    
    suggestions.sort(key=lambda x: x[0], reverse=True)
    
    if suggestions:
        cols = st.columns(3)
        for idx, (score, user) in enumerate(suggestions[:3]):
            with cols[idx % 3]:
                with st.container():
                    if user.get('profile_pic'):
                        st.image(user['profile_pic'], width=80)
                    else:
                        st.image("https://via.placeholder.com/80", width=80)
                    
                    st.markdown(f"**{user['first_name']} {user['last_name']}**")
                    st.caption(f"{user.get('current_position', '')}")
                    st.caption(f"{user.get('company', '')}")
                    
                    if st.button("Connect", key=f"suggest_{user['id']}", type="primary"):
                        from utils.database import add_friend_request
                        success, msg = add_friend_request(user_id, user['id'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("No connection suggestions available.")
