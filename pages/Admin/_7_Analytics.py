import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from utils.database import (
    get_user_statistics, get_platform_statistics, get_growth_data,
    get_all_users, get_confessions, get_events,
    get_announcements, get_contributions
)

def admin_analytics_page():
    """Admin Analytics Dashboard"""
    st.title("📊 Platform Analytics")
    
    # Get all data
    user_stats = get_user_statistics()
    platform_stats = get_platform_statistics()
    growth_data = get_growth_data(days=90)
    all_users = get_all_users()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "User Analytics", "Content Analytics", "Engagement"
    ])
    
    with tab1:
        # Overview Dashboard
        st.subheader("📈 Platform Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Users",
                user_stats['total_users'],
                f"+{user_stats['new_users_month']} this month"
            )
        
        with col2:
            active_rate = (user_stats['active_users'] / user_stats['total_users'] * 100) if user_stats['total_users'] > 0 else 0
            st.metric(
                "Active Users",
                user_stats['active_users'],
                f"{active_rate:.1f}% active"
            )
        
        with col3:
            st.metric(
                "Confessions",
                platform_stats['total_confessions']
            )
        
        with col4:
            st.metric(
                "Active Events",
                platform_stats['active_events']
            )
        
        # Growth chart
        st.markdown("### 📈 User Growth Trend")
        
        if growth_data:
            df_growth = pd.DataFrame(growth_data)
            
            if not df_growth.empty:
                fig = go.Figure()
                
                # Add traces for each user type
                fig.add_trace(go.Scatter(
                    x=df_growth['date'],
                    y=df_growth['new_users'],
                    mode='lines+markers',
                    name='New Users',
                    line=dict(color='#3B82F6', width=3)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_growth['date'],
                    y=df_growth['students'],
                    mode='lines',
                    name='Students',
                    line=dict(color='#10B981', width=2, dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_growth['date'],
                    y=df_growth['alumni'],
                    mode='lines',
                    name='Alumni',
                    line=dict(color='#8B5CF6', width=2, dash='dot')
                ))
                
                fig.update_layout(
                    title="Daily User Registration (Last 90 Days)",
                    xaxis_title="Date",
                    yaxis_title="New Users",
                    hovermode='x unified',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Platform health
        st.markdown("### 🏥 Platform Health")
        
        col_health1, col_health2, col_health3, col_health4 = st.columns(4)
        
        with col_health1:
            # Uptime (placeholder)
            uptime = "99.9%"
            st.metric("Uptime", uptime)
        
        with col_health2:
            # Response time (placeholder)
            response = "120ms"
            st.metric("Avg Response", response)
        
        with col_health3:
            # Error rate (placeholder)
            error_rate = "0.01%"
            st.metric("Error Rate", error_rate)
        
        with col_health4:
            # Satisfaction (placeholder)
            satisfaction = "4.8/5"
            st.metric("User Satisfaction", satisfaction)
    
    with tab2:
        # User Analytics
        st.subheader("👤 User Analytics")
        
        # User distribution
        col_dist1, col_dist2 = st.columns(2)
        
        with col_dist1:
            # Role distribution
            role_dist = user_stats.get('users_by_role', {})
            if role_dist:
                df_roles = pd.DataFrame(list(role_dist.items()), columns=['Role', 'Count'])
                df_roles['Role'] = df_roles['Role'].str.title()
                
                fig_roles = px.pie(df_roles, values='Count', names='Role',
                                 title="User Distribution by Role",
                                 hole=0.3)
                st.plotly_chart(fig_roles, use_container_width=True)
        
        with col_dist2:
            # Department distribution
            dept_dist = user_stats.get('users_by_department', {})
            if dept_dist:
                df_depts = pd.DataFrame(list(dept_dist.items()), columns=['Department', 'Count'])
                
                fig_depts = px.bar(df_depts, x='Department', y='Count',
                                 title="Users by Department",
                                 color='Count')
                fig_depts.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_depts, use_container_width=True)
        
        # User engagement
        st.markdown("### 📊 User Engagement Metrics")
        
        col_eng1, col_eng2, col_eng3, col_eng4 = st.columns(4)
        
        with col_eng1:
            # Daily active users (placeholder)
            dau = "245"
            st.metric("Daily Active", dau)
        
        with col_eng2:
            # Weekly active users (placeholder)
            wau = "1,245"
            st.metric("Weekly Active", wau)
        
        with col_eng3:
            # Monthly active users
            mau = user_stats['active_users']
            st.metric("Monthly Active", mau)
        
        with col_eng4:
            # Session duration (placeholder)
            session = "12m 34s"
            st.metric("Avg Session", session)
        
        # User retention
        st.markdown("### 📈 User Retention")
        
        # This would require cohort analysis
        st.info("User retention analytics coming soon!")
        
        # Geographic distribution (if data available)
        st.markdown("### 🌍 Geographic Distribution")
        
        # This would require location data
        st.info("Geographic analytics coming soon when users add location information.")
    
    with tab3:
        # Content Analytics
        st.subheader("📝 Content Analytics")
        
        # Content overview
        col_cont1, col_cont2, col_cont3, col_cont4 = st.columns(4)
        
        with col_cont1:
            st.metric("Confessions", platform_stats['total_confessions'])
        
        with col_cont2:
            st.metric("Messages", platform_stats['total_messages'])
        
        with col_cont3:
            st.metric("Groups", platform_stats['total_groups'])
        
        with col_cont4:
            st.metric("Events", platform_stats['active_events'])
        
        # Confession analytics
        st.markdown("### 💭 Confession Analytics")
        
        confessions = get_confessions(status='all', limit=1000)
        
        if confessions:
            # Status distribution
            status_counts = {}
            for conf in confessions:
                status = conf['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            df_status = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            df_status['Status'] = df_status['Status'].str.title()
            
            fig_status = px.pie(df_status, values='Count', names='Status',
                              title="Confessions by Status",
                              color='Status',
                              color_discrete_map={
                                  'Pending': '#F59E0B',
                                  'Approved': '#10B981',
                                  'Rejected': '#EF4444'
                              })
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Anonymous vs Named
            anonymous_count = len([c for c in confessions if c['is_anonymous'] == 1])
            named_count = len([c for c in confessions if c['is_anonymous'] == 0])
            
            df_anon = pd.DataFrame({
                'Type': ['Anonymous', 'Named'],
                'Count': [anonymous_count, named_count]
            })
            
            fig_anon = px.bar(df_anon, x='Type', y='Count',
                            title="Anonymous vs Named Confessions",
                            color='Type')
            st.plotly_chart(fig_anon, use_container_width=True)
        
        # Event analytics
        st.markdown("### 📅 Event Analytics")
        
        events = get_events(upcoming=False, limit=100)
        
        if events:
            # Event participation
            participation = [e['participant_count'] for e in events]
            avg_participation = sum(participation) / len(participation) if participation else 0
            
            col_event1, col_event2, col_event3 = st.columns(3)
            
            with col_event1:
                st.metric("Total Events", len(events))
            
            with col_event2:
                st.metric("Avg Participants", f"{avg_participation:.1f}")
            
            with col_event3:
                max_event = max(events, key=lambda x: x['participant_count']) if events else None
                if max_event:
                    st.metric("Most Popular", max_event['participant_count'])
        
        # Content growth over time
        st.markdown("### 📈 Content Growth")
        
        # This would require time-series data
        st.info("Content growth timeline coming soon!")
    
    with tab4:
        # Engagement Analytics
        st.subheader("📊 Engagement Analytics")
        
        # Engagement metrics
        col_eng1, col_eng2, col_eng3 = st.columns(3)
        
        with col_eng1:
            # Message frequency (placeholder)
            messages_per_day = "1,234"
            st.metric("Messages/Day", messages_per_day)
        
        with col_eng2:
            # Friend requests (placeholder)
            friend_requests = "56/day"
            st.metric("Friend Requests", friend_requests)
        
        with col_eng3:
            # Group activity (placeholder)
            group_posts = "89/day"
            st.metric("Group Posts", group_posts)
        
        # Time-based engagement
        st.markdown("### 🕒 Engagement by Time of Day")
        
        # This would require time-stamped activity data
        st.info("Time-based engagement analytics coming soon!")
        
        # Platform usage patterns
        st.markdown("### 📱 Platform Usage Patterns")
        
        col_pattern1, col_pattern2 = st.columns(2)
        
        with col_pattern1:
            # Device distribution (placeholder)
            st.info("Device analytics coming soon!")
        
        with col_pattern2:
            # Browser distribution (placeholder)
            st.info("Browser analytics coming soon!")
        
        # Feature usage
        st.markdown("### 🛠️ Feature Usage")
        
        # Get contributions data
        contributions = get_contributions()
        
        if contributions:
            # Contribution types
            type_counts = {}
            for contrib in contributions:
                contrib_type = contrib['type']
                type_counts[contrib_type] = type_counts.get(contrib_type, 0) + 1
            
            df_contrib_types = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Count'])
            df_contrib_types['Type'] = df_contrib_types['Type'].str.replace('_', ' ').str.title()
            
            fig_contrib = px.bar(df_contrib_types, x='Type', y='Count',
                               title="Alumni Contributions by Type",
                               color='Count')
            st.plotly_chart(fig_contrib, use_container_width=True)
        
        # User feedback and satisfaction
        st.markdown("### ⭐ User Satisfaction")
        
        col_sat1, col_sat2, col_sat3 = st.columns(3)
        
        with col_sat1:
            # Rating (placeholder)
            rating = "4.7"
            st.metric("Avg Rating", f"{rating}/5")
        
        with col_sat2:
            # Reviews (placeholder)
            reviews = "128"
            st.metric("Total Reviews", reviews)
        
        with col_sat3:
            # Support tickets (placeholder)
            tickets = "12"
            st.metric("Support Tickets", tickets)
    
    # Export and reporting
    st.markdown("---")
    st.subheader("📤 Reports & Exports")
    
    col_report1, col_report2, col_report3 = st.columns(3)
    
    with col_report1:
        if st.button("📄 Generate Monthly Report", use_container_width=True):
            st.info("Report generation coming soon!")
    
    with col_report2:
        if st.button("📊 Export Analytics Data", use_container_width=True):
            # Create sample export data
            export_data = {
                'metric': ['Total Users', 'Active Users', 'Confessions', 'Events'],
                'value': [user_stats['total_users'], user_stats['active_users'],
                         platform_stats['total_confessions'], platform_stats['active_events']]
            }
            
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="mes_analytics_export.csv",
                mime="text/csv"
            )
    
    with col_report3:
        if st.button("🚨 Generate Alerts Report", use_container_width=True):
            st.info("Alerts report coming soon!")
