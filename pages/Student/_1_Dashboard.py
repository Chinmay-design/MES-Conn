import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from utils.database import (
    get_student_profile, get_events, get_confessions,
    get_friends, get_all_users, get_announcements,
    get_user_statistics, get_platform_statistics,
    get_notifications, get_user_by_id
)

def student_dashboard_page(user_id):
    """Student Dashboard"""
    st.title("🎓 Student Dashboard")
    
    # Get user profile
    profile = get_student_profile(user_id)
    
    if not profile:
        st.error("Profile not found")
        return
    
    # Welcome section with quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Friends", len(get_friends(user_id)))
    
    with col2:
        events = get_events(upcoming=True, user_id=user_id)
        st.metric("Upcoming Events", len([e for e in events if e.get('is_registered')]))
    
    with col3:
        confessions = get_confessions(status='approved', limit=100)
        st.metric("Confessions", len(confessions))
    
    with col4:
        notifications = get_notifications(user_id, unread_only=True)
        st.metric("Unread Notifications", len(notifications))
    
    st.markdown("---")
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Announcements
        st.subheader("📢 Latest Announcements")
        announcements = get_announcements(target_role='student', limit=5)
        
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
        st.subheader("📅 Upcoming Events")
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
                            if st.button("Register", key=f"reg_{event['id']}"):
                                from utils.database import register_for_event
                                success, msg = register_for_event(event['id'], user_id)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                    st.markdown("---")
        else:
            st.info("No upcoming events.")
    
    with col2:
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        quick_actions = [
            ("📝 Post Confession", "Student/Confessions"),
            ("👥 Find Friends", "Student/Friends"),
            ("💬 Start Chat", "Student/Chat"),
            ("👥 Join Group", "Student/Groups"),
            ("📅 Create Event", "Student/Events"),
            ("📚 View Resources", "#"),
            ("📊 View Analytics", "#"),
            ("⚙️ Settings", "Student/Settings")
        ]
        
        for action_text, action_page in quick_actions:
            if st.button(action_text, use_container_width=True, key=f"quick_{action_text}"):
                if action_page.startswith("#"):
                    st.info(f"{action_text} feature coming soon!")
                else:
                    st.session_state.current_page = action_page
                    st.rerun()
        
        # Recent Friends Activity
        st.subheader("👥 Friend Activity")
        friends = get_friends(user_id)[:5]
        
        if friends:
            for friend in friends:
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.markdown(f"**{friend['first_name']} {friend['last_name']}**")
                    st.caption(f"{friend.get('department', '')}")
                with col_f2:
                    if st.button("💬", key=f"chat_{friend['id']}"):
                        st.session_state.chat_with = friend['id']
                        st.session_state.current_page = "Student/Chat"
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No friends yet. Add some friends!")
        
        # Platform Statistics
        st.subheader("📊 Platform Stats")
        stats = get_user_statistics()
        platform_stats = get_platform_statistics()
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Total Students", stats['users_by_role'].get('student', 0))
            st.metric("Active Events", platform_stats['active_events'])
        
        with col_s2:
            st.metric("Total Alumni", stats['users_by_role'].get('alumni', 0))
            st.metric("Active Jobs", platform_stats['active_jobs'])
    
    # Recent Confessions
    st.markdown("---")
    st.subheader("💭 Recent Confessions")
    
    confessions = get_confessions(status='approved', limit=5)
    
    if confessions:
        cols = st.columns(len(confessions))
        for idx, confession in enumerate(confessions):
            with cols[idx % len(cols)]:
                with st.container():
                    st.markdown(f"<div class='confession-card'>", unsafe_allow_html=True)
                    if confession['is_anonymous']:
                        author = "Anonymous"
                        avatar = "👤"
                    else:
                        author = f"{confession.get('first_name', 'User')}"
                        avatar = "👤"
                    
                    st.markdown(f"{avatar} **{author}**")
                    st.markdown(f"> {confession['content'][:100]}...")
                    
                    col_c1, col_c2 = st.columns([1, 1])
                    with col_c1:
                        st.caption(f"❤️ {confession.get('like_count', 0)}")
                    with col_c2:
                        st.caption(f"{confession['created_at'][:10]}")
                    
                    if st.button("View", key=f"view_conf_{confession['id']}"):
                        st.session_state.current_page = "Student/Confessions"
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No confessions yet. Be the first to post!")
    
    # Study Groups
    st.markdown("---")
    st.subheader("👥 Popular Study Groups")
    
    from utils.database import get_groups
    groups = get_groups(user_id=user_id)[:3]
    
    if groups:
        cols = st.columns(len(groups))
        for idx, group in enumerate(groups):
            with cols[idx % len(cols)]:
                with st.container():
                    st.markdown(f"<div class='group-card'>", unsafe_allow_html=True)
                    st.markdown(f"**{group['name']}**")
                    st.caption(f"{group.get('description', '')[:50]}...")
                    st.caption(f"👥 {group['member_count']} members • {group['category']}")
                    
                    if group.get('user_role'):
                        st.success(f"Member ({group['user_role']})")
                    else:
                        if st.button("Join", key=f"join_{group['id']}"):
                            from utils.database import join_group
                            if join_group(group['id'], user_id):
                                st.success("Joined successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to join group")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No groups available. Create one!")
    
    # Job Opportunities (if any)
    st.markdown("---")
    st.subheader("💼 Recent Job Postings")
    
    from utils.database import get_job_postings
    jobs = get_job_postings(limit=3)
    
    if jobs:
        for job in jobs:
            with st.container():
                col_j1, col_j2 = st.columns([3, 1])
                with col_j1:
                    st.markdown(f"**{job['position']} at {job['company']}**")
                    st.caption(f"📍 {job['location'] or 'Remote'} • 💰 {job['salary_range'] or 'Competitive'}")
                    st.caption(f"Posted by {job['first_name']} {job['last_name']}")
                with col_j2:
                    if st.button("Apply", key=f"apply_{job['id']}"):
                        st.session_state.current_page = "Student/Jobs"
                        st.rerun()
                st.markdown("---")
    else:
        st.info("No job postings available currently.")
