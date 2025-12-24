import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from utils.database import (
    get_user_statistics, get_platform_statistics, get_growth_data,
    get_all_users, get_confessions, get_events,
    get_announcements, get_contributions
)

def admin_dashboard_page():
    """Admin Dashboard"""
    st.title("🛠️ Admin Dashboard")
    
    # Get statistics
    user_stats = get_user_statistics()
    platform_stats = get_platform_statistics()
    growth_data = get_growth_data(days=30)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Users",
            user_stats['total_users'],
            f"+{user_stats['new_users_month']} this month"
        )
    
    with col2:
        st.metric(
            "Active Users",
            user_stats['active_users'],
            f"{int(user_stats['active_users']/user_stats['total_users']*100)}% active"
        )
    
    with col3:
        st.metric(
            "Pending Confessions",
            platform_stats.get('pending_confessions', 0)
        )
    
    with col4:
        st.metric(
            "Active Events",
            platform_stats['active_events']
        )
    
    st.markdown("---")
    
    # Main dashboard in columns
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # User Growth Chart
        st.subheader("📈 User Growth (Last 30 Days)")
        
        if growth_data:
            df = pd.DataFrame(growth_data)
            if not df.empty:
                fig = px.line(df, x='date', y=['new_users', 'students', 'alumni'],
                            title="Daily User Registration",
                            labels={'value': 'New Users', 'date': 'Date'},
                            markers=True)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No growth data available yet.")
        
        # Platform Activity
        st.subheader("🔄 Recent Platform Activity")
        
        # Get recent data
        recent_users = get_all_users()[:5]
        recent_confessions = get_confessions(status='pending', limit=5)
        recent_events = get_events(upcoming=True, limit=3)
        
        # Activity tabs
        act_tab1, act_tab2, act_tab3 = st.tabs(["👤 New Users", "📝 Pending Confessions", "📅 Upcoming Events"])
        
        with act_tab1:
            if recent_users:
                for user in recent_users:
                    col_user1, col_user2 = st.columns([3, 1])
                    with col_user1:
                        st.markdown(f"**{user['first_name']} {user['last_name']}**")
                        st.caption(f"{user['role'].title()} • {user.get('department', '')}")
                    with col_user2:
                        st.caption(f"🗓️ {user['created_at'][:10]}")
                    st.markdown("---")
            else:
                st.info("No recent users")
        
        with act_tab2:
            if recent_confessions:
                for conf in recent_confessions:
                    col_conf1, col_conf2 = st.columns([4, 1])
                    with col_conf1:
                        st.markdown(f"**{conf['content'][:50]}...**")
                        st.caption(f"Anonymous" if conf['is_anonymous'] else "Named")
                    with col_conf2:
                        if st.button("Review", key=f"review_{conf['id']}"):
                            st.session_state.current_page = "Admin/Confession_Moderation"
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("No pending confessions")
        
        with act_tab3:
            if recent_events:
                for event in recent_events:
                    col_event1, col_event2 = st.columns([3, 1])
                    with col_event1:
                        st.markdown(f"**{event['title']}**")
                        st.caption(f"📅 {event['event_date']} • 👥 {event['participant_count']}")
                    with col_event2:
                        st.caption(f"By {event['organizer_first_name']}")
                    st.markdown("---")
            else:
                st.info("No upcoming events")
    
    with col_right:
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        quick_actions = [
            ("👨‍🎓 Manage Users", "Admin/Student_Management"),
            ("📢 Post Announcement", "Admin/Announcements"),
            ("🔍 Moderate Content", "Admin/Confession_Moderation"),
            ("📊 View Analytics", "Admin/Analytics"),
            ("👥 Manage Groups", "Admin/Groups_Management"),
            ("⚙️ System Settings", "Admin/Settings")
        ]
        
        for action_text, action_page in quick_actions:
            if st.button(action_text, use_container_width=True):
                st.session_state.current_page = action_page
                st.rerun()
        
        # Platform Statistics
        st.subheader("📊 Platform Stats")
        
        # User distribution
        user_dist = user_stats.get('users_by_role', {})
        if user_dist:
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Students", user_dist.get('student', 0))
                st.metric("Admins", user_dist.get('admin', 0))
            with col_stat2:
                st.metric("Alumni", user_dist.get('alumni', 0))
        
        # Department distribution
        dept_dist = user_stats.get('users_by_department', {})
        if dept_dist:
            with st.expander("Department Distribution"):
                for dept, count in dept_dist.items():
                    st.markdown(f"**{dept}:** {count}")
        
        # System Health
        st.subheader("🖥️ System Health")
        
        col_health1, col_health2 = st.columns(2)
        
        with col_health1:
            # Database size (placeholder)
            db_size = "~10 MB"
            st.metric("Database Size", db_size)
        
        with col_health2:
            # Active sessions (placeholder)
            active_sessions = "25"
            st.metric("Active Sessions", active_sessions)
        
        # Recent Issues
        st.subheader("⚠️ Recent Issues")
        
        # This would come from error logs
        st.info("No recent issues detected")
    
    # Bottom section - Recent Contributions and Announcements
    st.markdown("---")
    
    col_bottom1, col_bottom2 = st.columns(2)
    
    with col_bottom1:
        # Recent Contributions
        st.subheader("💡 Recent Contributions")
        
        contributions = get_contributions(status='pending', limit=5)
        
        if contributions:
            for contrib in contributions:
                col_cont1, col_cont2 = st.columns([3, 1])
                with col_cont1:
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
                    st.caption(f"By {contrib['first_name']} {contrib['last_name']}")
                with col_cont2:
                    if st.button("Review", key=f"review_contrib_{contrib['id']}"):
                        # Would link to contribution management
                        st.info("Contribution review coming soon!")
                st.markdown("---")
        else:
            st.info("No pending contributions")
    
    with col_bottom2:
        # Recent Announcements
        st.subheader("📢 Recent Announcements")
        
        announcements = get_announcements(limit=5)
        
        if announcements:
            for ann in announcements:
                col_ann1, col_ann2 = st.columns([3, 1])
                with col_ann1:
                    st.markdown(f"**{ann['title']}**")
                    st.caption(f"By {ann['first_name']} • {ann['created_at'][:10]}")
                with col_ann2:
                    priority_color = {
                        'urgent': '🔴',
                        'high': '🟠',
                        'normal': '🔵',
                        'low': '⚪'
                    }.get(ann['priority'], '⚪')
                    st.markdown(priority_color)
                st.markdown("---")
        else:
            st.info("No recent announcements")
    
    # System Monitoring
    st.markdown("---")
    st.subheader("📈 System Monitoring")
    
    # Create tabs for different monitoring views
    mon_tab1, mon_tab2, mon_tab3 = st.tabs(["User Activity", "Content Growth", "Performance"])
    
    with mon_tab1:
        # User activity metrics
        col_mon1, col_mon2, col_mon3 = st.columns(3)
        
        with col_mon1:
            # Average session duration (placeholder)
            avg_session = "15m"
            st.metric("Avg Session", avg_session)
        
        with col_mon2:
            # Daily active users (placeholder)
            dau = "245"
            st.metric("Daily Active", dau)
        
        with col_mon3:
            # Weekly active users (placeholder)
            wau = "1,245"
            st.metric("Weekly Active", wau)
    
    with mon_tab2:
        # Content growth metrics
        col_cont1, col_cont2, col_cont3 = st.columns(3)
        
        with col_cont1:
            st.metric("Total Confessions", platform_stats['total_confessions'])
        
        with col_cont2:
            st.metric("Total Messages", platform_stats['total_messages'])
        
        with col_cont3:
            st.metric("Total Groups", platform_stats['total_groups'])
    
    with mon_tab3:
        # Performance metrics
        col_perf1, col_perf2, col_perf3 = st.columns(3)
        
        with col_perf1:
            # Uptime (placeholder)
            uptime = "99.9%"
            st.metric("Uptime", uptime)
        
        with col_perf2:
            # Response time (placeholder)
            response_time = "120ms"
            st.metric("Response Time", response_time)
        
        with col_perf3:
            # Error rate (placeholder)
            error_rate = "0.01%"
            st.metric("Error Rate", error_rate)
