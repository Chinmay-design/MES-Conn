import streamlit as st
from utils.database import (
    get_confessions, update_confession_status,
    get_user_by_id
)

def admin_confession_moderation_page():
    """Confession Moderation Page for Admin"""
    st.title("🔍 Confession Moderation")
    
    # Get pending confessions
    pending_confessions = get_confessions(status='pending', limit=100)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Pending Review", "Approved", "Rejected"])
    
    with tab1:
        # Pending Review
        st.subheader("⏳ Pending Confessions")
        
        if pending_confessions:
            st.markdown(f"**Total Pending:** {len(pending_confessions)}")
            
            for confession in pending_confessions:
                display_confession_for_moderation(confession)
        else:
            st.success("🎉 No pending confessions to review!")
    
    with tab2:
        # Approved Confessions
        st.subheader("✅ Approved Confessions")
        
        approved_confessions = get_confessions(status='approved', limit=50)
        
        if approved_confessions:
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                date_filter = st.selectbox(
                    "Filter by date",
                    ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
                )
            
            with col_filter2:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Newest", "Most Liked", "Oldest"]
                )
            
            # Apply filters (simplified)
            filtered_confessions = approved_confessions
            
            # Sort
            if sort_by == "Newest":
                filtered_confessions.sort(key=lambda x: x['created_at'], reverse=True)
            elif sort_by == "Most Liked":
                filtered_confessions.sort(key=lambda x: x.get('like_count', 0), reverse=True)
            elif sort_by == "Oldest":
                filtered_confessions.sort(key=lambda x: x['created_at'])
            
            # Display
            for confession in filtered_confessions[:20]:  # Limit display
                display_confession_card_mod(confession, show_actions=False)
        else:
            st.info("No approved confessions yet.")
    
    with tab3:
        # Rejected Confessions
        st.subheader("❌ Rejected Confessions")
        
        rejected_confessions = get_confessions(status='rejected', limit=50)
        
        if rejected_confessions:
            for confession in rejected_confessions:
                display_confession_card_mod(confession, show_actions=True)
        else:
            st.info("No rejected confessions.")
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Moderation Statistics")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Pending", len(pending_confessions))
    
    with col_stat2:
        approved_count = len(get_confessions(status='approved', limit=1000))
        st.metric("Approved", approved_count)
    
    with col_stat3:
        rejected_count = len(get_confessions(status='rejected', limit=1000))
        st.metric("Rejected", rejected_count)
    
    with col_stat4:
        total = len(pending_confessions) + approved_count + rejected_count
        approval_rate = (approved_count / total * 100) if total > 0 else 0
        st.metric("Approval Rate", f"{approval_rate:.1f}%")
    
    # Moderation guidelines
    with st.expander("📋 Moderation Guidelines", expanded=True):
        st.markdown("""
        ### Community Guidelines
        
        **✅ APPROVE if confession:**
        - Is respectful and positive
        - Shares genuine feelings or experiences
        - Follows community standards
        - Doesn't target specific individuals
        - Is appropriate for all audiences
        
        **❌ REJECT if confession:**
        - Contains hate speech or discrimination
        - Targets or harasses individuals
        - Shares personal information
        - Promotes illegal activities
        - Contains explicit content
        - Is spam or advertisement
        - Violates platform rules
        
        **⚠️ USE CAUTION with:**
        - Sensitive topics (handle with care)
        - Political or controversial content
        - Mental health mentions (ensure supportive)
        
        **Moderation Tips:**
        - Consider context and intent
        - Be consistent with decisions
        - When in doubt, discuss with team
        - Always prioritize community safety
        """)

def display_confession_for_moderation(confession):
    """Display a confession for moderation with action buttons"""
    with st.container():
        st.markdown(f"<div style='background: white; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #F59E0B;'>", unsafe_allow_html=True)
        
        # Confession header
        col_head1, col_head2 = st.columns([4, 1])
        
        with col_head1:
            # Author info
            if confession['is_anonymous']:
                author = "Anonymous"
                avatar = "👤"
            else:
                if confession.get('user_id'):
                    user = get_user_by_id(confession['user_id'])
                    if user:
                        author = f"{user['first_name']} {user['last_name']} (ID: {user['id']})"
                    else:
                        author = "User (deleted)"
                else:
                    author = "User"
                avatar = "👤"
            
            st.markdown(f"{avatar} **{author}**")
            
            # Tags
            if confession.get('tags'):
                tags = confession['tags'].split(',')
                tag_text = " ".join([f"`#{tag}`" for tag in tags])
                st.markdown(tag_text)
        
        with col_head2:
            # Date
            st.caption(f"📅 {confession['created_at'][:10]}")
            st.caption(f"🕒 {confession['created_at'][11:16]}")
        
        # Confession content
        st.markdown(f"### Content")
        st.markdown(f"> *{confession['content']}*")
        
        # Additional info
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.caption(f"**Confession ID:** `{confession['id']}`")
            st.caption(f"**Anonymous:** {'Yes' if confession['is_anonymous'] else 'No'}")
        
        with col_info2:
            st.caption(f"**Length:** {len(confession['content'])} characters")
            st.caption(f"**Submitted:** {confession['created_at'][:19]}")
        
        # Moderation actions
        st.markdown("### 🛠️ Moderation Actions")
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("✅ Approve", key=f"approve_{confession['id']}", type="primary", use_container_width=True):
                if update_confession_status(confession['id'], 'approved'):
                    st.success("Confession approved!")
                    st.rerun()
                else:
                    st.error("Failed to approve confession")
        
        with col_action2:
            if st.button("❌ Reject", key=f"reject_{confession['id']}", type="secondary", use_container_width=True):
                # Show rejection reasons
                with st.form(f"reject_form_{confession['id']}"):
                    rejection_reason = st.selectbox(
                        "Rejection Reason",
                        ["Violates community guidelines", "Contains inappropriate content", 
                         "Targets individuals", "Spam or advertisement", "Other"]
                    )
                    
                    custom_reason = st.text_area("Additional notes (optional)")
                    
                    if st.form_submit_button("Confirm Rejection"):
                        if update_confession_status(confession['id'], 'rejected'):
                            st.success("Confession rejected")
                            st.rerun()
                        else:
                            st.error("Failed to reject confession")
        
        with col_action3:
            if st.button("🔍 View Details", key=f"details_{confession['id']}", use_container_width=True):
                with st.expander("Additional Details", expanded=True):
                    # Show user info if not anonymous
                    if not confession['is_anonymous'] and confession.get('user_id'):
                        user = get_user_by_id(confession['user_id'])
                        if user:
                            st.markdown("### 👤 User Information")
                            st.markdown(f"**Name:** {user['first_name']} {user['last_name']}")
                            st.markdown(f"**Email:** {user['email']}")
                            st.markdown(f"**Role:** {user['role'].title()}")
                            st.markdown(f"**Joined:** {user['created_at'][:10]}")
                    
                    # Similar confessions (by tags or content)
                    st.markdown("### 🔍 Similar Confessions")
                    st.info("Similarity analysis coming soon!")
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_confession_card_mod(confession, show_actions=True):
    """Display a confession card for moderation view"""
    with st.container():
        status_colors = {
            'approved': '🟢',
            'rejected': '🔴',
            'pending': '🟡'
        }
        status_icon = status_colors.get(confession['status'], '⚪')
        
        st.markdown(f"<div style='background: white; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid {'#10B981' if confession['status'] == 'approved' else '#EF4444' if confession['status'] == 'rejected' else '#F59E0B'};'>", unsafe_allow_html=True)
        
        # Header
        col_head1, col_head2 = st.columns([4, 1])
        
        with col_head1:
            st.markdown(f"**Confession ID:** `{confession['id']}`")
            st.caption(f"{status_icon} {confession['status'].upper()} • {'Anonymous' if confession['is_anonymous'] else 'Named'}")
        
        with col_head2:
            st.caption(f"📅 {confession['created_at'][:10]}")
        
        # Content preview
        content_preview = confession['content'][:100] + "..." if len(confession['content']) > 100 else confession['content']
        st.markdown(f"> {content_preview}")
        
        # User info if not anonymous
        if not confession['is_anonymous'] and confession.get('user_id'):
            user = get_user_by_id(confession['user_id'])
            if user:
                st.caption(f"👤 By: {user['first_name']} {user['last_name']} ({user['role'].title()})")
        
        # Actions for rejected confessions
        if show_actions and confession['status'] == 'rejected':
            col_act1, col_act2 = st.columns(2)
            
            with col_act1:
                if st.button("Restore", key=f"restore_{confession['id']}"):
                    if update_confession_status(confession['id'], 'approved'):
                        st.success("Confession restored!")
                        st.rerun()
            
            with col_act2:
                if st.button("Delete Permanently", key=f"perm_del_{confession['id']}", type="secondary"):
                    st.warning("Permanently delete this confession?")
                    if st.button("Confirm Delete", key=f"confirm_perm_{confession['id']}"):
                        st.info("Permanent delete feature coming soon!")
        
        st.markdown("</div>", unsafe_allow_html=True)
