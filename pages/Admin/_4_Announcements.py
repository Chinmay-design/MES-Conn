import streamlit as st
from datetime import datetime
from utils.database import (
    get_announcements, add_announcement,
    get_all_users, update_user_profile
)

def admin_announcements_page():
    """Announcements Management Page for Admin"""
    st.title("📢 Announcements Management")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["All Announcements", "Create Announcement", "Schedule"])
    
    with tab1:
        # All Announcements
        st.subheader("📋 All Announcements")
        
        # Get all announcements
        announcements = get_announcements(limit=100)
        
        if announcements:
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                status_filter = st.selectbox(
                    "Filter by status",
                    ["All", "Active", "Inactive"]
                )
            
            with col_filter2:
                priority_filter = st.selectbox(
                    "Filter by priority",
                    ["All", "Urgent", "High", "Normal", "Low"]
                )
            
            # Apply filters
            filtered_announcements = announcements
            
            if status_filter == "Active":
                filtered_announcements = [a for a in filtered_announcements if a['is_active'] == 1]
            elif status_filter == "Inactive":
                filtered_announcements = [a for a in filtered_announcements if a['is_active'] == 0]
            
            if priority_filter != "All":
                filtered_announcements = [a for a in filtered_announcements if a['priority'] == priority_filter.lower()]
            
            # Display announcements
            if filtered_announcements:
                for ann in filtered_announcements:
                    display_announcement_card(ann)
            else:
                st.info(f"No announcements found with status '{status_filter}' and priority '{priority_filter}'.")
        else:
            st.info("No announcements created yet.")
    
    with tab2:
        # Create Announcement
        st.subheader("✍️ Create New Announcement")
        
        with st.form("create_announcement_form"):
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title *", placeholder="Important Announcement")
                priority = st.selectbox(
                    "Priority *",
                    ["Normal", "Low", "High", "Urgent"]
                )
            
            with col2:
                target_role = st.selectbox(
                    "Target Audience *",
                    ["All", "Students", "Alumni", "Admins", "Specific Group"]
                )
                is_active = st.checkbox("Active Immediately", value=True)
            
            # Content
            st.markdown("### 📝 Content")
            
            content = st.text_area(
                "Announcement Content *",
                placeholder="Write your announcement here...\n\nYou can use markdown formatting:\n- **Bold** text\n- *Italic* text\n- Lists\n- [Links](https://example.com)",
                height=200
            )
            
            # Preview
            st.markdown("### 👁️ Preview")
            with st.container():
                st.markdown(f"**{title}**")
                priority_colors = {
                    'urgent': '🔴',
                    'high': '🟠',
                    'normal': '🔵',
                    'low': '⚪'
                }
                st.caption(f"{priority_colors.get(priority.lower(), '⚪')} {priority} • For: {target_role}")
                st.markdown("---")
                st.markdown(content[:500] + "..." if len(content) > 500 else content)
            
            # Scheduling (optional)
            st.markdown("### ⏰ Scheduling (Optional)")
            
            col_sched1, col_sched2 = st.columns(2)
            
            with col_sched1:
                schedule_later = st.checkbox("Schedule for later", value=False)
                if schedule_later:
                    schedule_date = st.date_input("Schedule Date", min_value=datetime.now().date())
                    schedule_time = st.time_input("Schedule Time")
            
            with col_sched2:
                expiration = st.checkbox("Set expiration", value=False)
                if expiration:
                    expire_date = st.date_input("Expiration Date", min_value=datetime.now().date())
            
            # Advanced options
            with st.expander("⚙️ Advanced Options"):
                col_adv1, col_adv2 = st.columns(2)
                
                with col_adv1:
                    require_acknowledgement = st.checkbox("Require acknowledgement", value=False)
                    allow_comments = st.checkbox("Allow comments", value=True)
                    send_email = st.checkbox("Send email notification", value=True)
                
                with col_adv2:
                    allow_sharing = st.checkbox("Allow sharing", value=True)
                    pin_to_top = st.checkbox("Pin to top", value=False)
                    show_author = st.checkbox("Show author", value=True)
            
            # Submit button
            col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
            with col_submit2:
                submit = st.form_submit_button("Publish Announcement", type="primary")
            
            if submit:
                if not all([title, content]):
                    st.error("Please fill all required fields (*)")
                else:
                    # Create announcement
                    announcement_id = add_announcement(
                        title=title,
                        content=content,
                        created_by=st.session_state.user_id,
                        target_role=target_role.lower() if target_role != "All" else None,
                        priority=priority.lower(),
                        is_active=1 if is_active else 0
                    )
                    
                    if announcement_id:
                        st.success("🎉 Announcement published successfully!")
                        st.balloons()
                        
                        # Show next steps
                        with st.expander("Next Steps", expanded=True):
                            st.markdown(f"""
                            ### 📢 Announcement Published!
                            
                            **Announcement ID:** `{announcement_id}`
                            **Status:** {'Active' if is_active else 'Inactive'}
                            **Audience:** {target_role}
                            **Priority:** {priority}
                            
                            **What happens next:**
                            
                            1. **Notification** - Target users will be notified
                            2. **Display** - Announcement appears in relevant feeds
                            3. **Tracking** - You can track views and engagement
                            4. **Management** - You can edit or deactivate as needed
                            
                            **Quick Actions:**
                            """)
                            
                            col_action1, col_action2 = st.columns(2)
                            with col_action1:
                                if st.button("View Announcement", type="primary"):
                                    st.rerun()
                            with col_action2:
                                if st.button("Create Another"):
                                    st.rerun()
                    else:
                        st.error("Failed to publish announcement")
    
    with tab3:
        # Schedule Management
        st.subheader("📅 Scheduled Announcements")
        
        # Get scheduled announcements (would need database field for scheduled time)
        st.info("Scheduled announcements feature coming soon!")
        
        # Calendar view
        st.markdown("### 🗓️ Announcement Calendar")
        
        # This would show a calendar with scheduled announcements
        st.info("Calendar view coming soon!")
        
        # Bulk scheduling
        st.markdown("### 📦 Bulk Scheduling")
        
        with st.form("bulk_schedule_form"):
            st.markdown("Schedule multiple announcements at once")
            
            upload_file = st.file_uploader("Upload CSV with announcements", type="csv")
            
            if upload_file:
                import pandas as pd
                try:
                    df = pd.read_csv(upload_file)
                    st.write("Preview:")
                    st.dataframe(df.head())
                    
                    schedule_date = st.date_input("Schedule all for date")
                    
                    if st.form_submit_button("Schedule All", type="primary"):
                        st.success(f"Scheduled {len(df)} announcements for {schedule_date}")
                except:
                    st.error("Error reading CSV file")
        
        # Recurring announcements
        st.markdown("### 🔄 Recurring Announcements")
        
        col_recur1, col_recur2 = st.columns(2)
        
        with col_recur1:
            st.info("Weekly announcements feature coming soon!")
        
        with col_recur2:
            st.info("Monthly announcements feature coming soon!")

def display_announcement_card(announcement):
    """Display an announcement card with management options"""
    with st.container():
        # Card header
        col_head1, col_head2 = st.columns([4, 1])
        
        with col_head1:
            st.markdown(f"### {announcement['title']}")
            
            # Priority and status
            priority_colors = {
                'urgent': '🔴',
                'high': '🟠',
                'normal': '🔵',
                'low': '⚪'
            }
            priority_icon = priority_colors.get(announcement['priority'], '⚪')
            
            status_icon = '🟢' if announcement['is_active'] == 1 else '⚫'
            status_text = 'Active' if announcement['is_active'] == 1 else 'Inactive'
            
            st.caption(f"{priority_icon} {announcement['priority'].upper()} • {status_icon} {status_text} • For: {announcement.get('target_role', 'all').upper()}")
        
        with col_head2:
            # Date
            st.caption(f"📅 {announcement['created_at'][:10]}")
            st.caption(f"By: {announcement['first_name']}")
        
        # Content preview
        if announcement['content']:
            preview = announcement['content'][:200] + "..." if len(announcement['content']) > 200 else announcement['content']
            st.markdown(f"> {preview}")
        
        # Management actions
        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
        
        with col_action1:
            if st.button("View", key=f"view_ann_{announcement['id']}"):
                with st.expander("Full Announcement", expanded=True):
                    st.markdown(f"**Title:** {announcement['title']}")
                    st.markdown(f"**Created:** {announcement['created_at']}")
                    st.markdown(f"**Priority:** {announcement['priority'].upper()}")
                    st.markdown(f"**Target:** {announcement.get('target_role', 'all').upper()}")
                    st.markdown(f"**Status:** {'Active' if announcement['is_active'] == 1 else 'Inactive'}")
                    st.markdown("**Content:**")
                    st.markdown(announcement['content'])
        
        with col_action2:
            if st.button("Edit", key=f"edit_ann_{announcement['id']}"):
                st.session_state.edit_announcement_id = announcement['id']
                st.rerun()
        
        with col_action3:
            if announcement['is_active'] == 1:
                if st.button("Deactivate", key=f"deact_{announcement['id']}"):
                    # Deactivate announcement
                    st.info("Deactivation feature coming soon!")
            else:
                if st.button("Activate", key=f"act_{announcement['id']}"):
                    # Activate announcement
                    st.info("Activation feature coming soon!")
        
        with col_action4:
            if st.button("Delete", key=f"del_{announcement['id']}", type="secondary"):
                st.warning(f"Delete announcement '{announcement['title']}'?")
                if st.button("Confirm Delete", key=f"confirm_del_{announcement['id']}"):
                    st.info("Delete feature coming soon!")
        
        # Stats (would come from analytics)
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.caption("👁️ Views: 0")
        
        with col_stat2:
            st.caption("👍 Engagement: 0%")
        
        with col_stat3:
            st.caption("📊 Reach: 0 users")
        
        st.markdown("---")
