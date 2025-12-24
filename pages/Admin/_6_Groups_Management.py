import streamlit as st
import pandas as pd
from utils.database import (
    get_groups, get_group_members, get_user_by_id
)

def admin_groups_management_page():
    """Groups Management Page for Admin"""
    st.title("👥 Groups Management")
    
    # Get all groups
    groups = get_groups()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["All Groups", "Group Analytics", "Group Policies"])
    
    with tab1:
        # All Groups
        st.subheader("📋 All Groups")
        
        if groups:
            # Search and filters
            col_search1, col_search2, col_search3 = st.columns(3)
            
            with col_search1:
                search_term = st.text_input("🔍 Search groups")
            
            with col_search2:
                category_filter = st.selectbox(
                    "Filter by category",
                    ["All"] + list(set([g.get('category', '') for g in groups if g.get('category')]))
                )
            
            with col_search3:
                visibility_filter = st.selectbox(
                    "Filter by visibility",
                    ["All", "Public", "Private"]
                )
            
            # Apply filters
            filtered_groups = groups
            
            if search_term:
                filtered_groups = [
                    g for g in filtered_groups 
                    if search_term.lower() in g['name'].lower()
                    or search_term.lower() in g.get('description', '').lower()
                ]
            
            if category_filter != "All":
                filtered_groups = [g for g in filtered_groups if g.get('category') == category_filter]
            
            if visibility_filter != "All":
                is_public = 1 if visibility_filter == "Public" else 0
                filtered_groups = [g for g in filtered_groups if g['is_public'] == is_public]
            
            # Display groups
            if filtered_groups:
                st.markdown(f"**Total Groups:** {len(filtered_groups)}")
                
                for group in filtered_groups:
                    display_group_admin_card(group)
            else:
                st.info("No groups found with the current filters.")
        else:
            st.info("No groups created yet.")
    
    with tab2:
        # Group Analytics
        st.subheader("📊 Group Analytics")
        
        if groups:
            # Overall stats
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                total_groups = len(groups)
                st.metric("Total Groups", total_groups)
            
            with col_stat2:
                public_groups = len([g for g in groups if g['is_public'] == 1])
                st.metric("Public Groups", public_groups)
            
            with col_stat3:
                private_groups = len([g for g in groups if g['is_public'] == 0])
                st.metric("Private Groups", private_groups)
            
            with col_stat4:
                total_members = sum(g['member_count'] for g in groups)
                avg_members = total_members / total_groups if total_groups > 0 else 0
                st.metric("Avg Members", f"{avg_members:.1f}")
            
            # Category distribution
            st.markdown("### 📈 Category Distribution")
            
            category_counts = {}
            for group in groups:
                category = group.get('category', 'general')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            if category_counts:
                import plotly.express as px
                
                df_categories = pd.DataFrame(list(category_counts.items()), columns=['Category', 'Count'])
                df_categories['Category'] = df_categories['Category'].str.title()
                
                fig = px.pie(df_categories, values='Count', names='Category',
                           title="Groups by Category")
                st.plotly_chart(fig, use_container_width=True)
            
            # Member distribution
            st.markdown("### 👥 Member Distribution")
            
            # Get groups by member count ranges
            member_ranges = {
                "1-10": 0,
                "11-50": 0,
                "51-100": 0,
                "101-500": 0,
                "500+": 0
            }
            
            for group in groups:
                members = group['member_count']
                if members <= 10:
                    member_ranges["1-10"] += 1
                elif members <= 50:
                    member_ranges["11-50"] += 1
                elif members <= 100:
                    member_ranges["51-100"] += 1
                elif members <= 500:
                    member_ranges["101-500"] += 1
                else:
                    member_ranges["500+"] += 1
            
            df_members = pd.DataFrame(list(member_ranges.items()), columns=['Member Range', 'Count'])
            
            fig = px.bar(df_members, x='Member Range', y='Count',
                       title="Groups by Member Count Range")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top groups by members
            st.markdown("### 🏆 Top Groups by Members")
            
            top_groups = sorted(groups, key=lambda x: x['member_count'], reverse=True)[:10]
            
            if top_groups:
                df_top = pd.DataFrame([{
                    'Name': g['name'],
                    'Category': g.get('category', 'general').title(),
                    'Members': g['member_count'],
                    'Visibility': 'Public' if g['is_public'] == 1 else 'Private',
                    'Created': g['created_at'][:10]
                } for g in top_groups])
                
                st.dataframe(
                    df_top,
                    column_config={
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Category": st.column_config.TextColumn("Category", width="small"),
                        "Members": st.column_config.NumberColumn("Members", width="small"),
                        "Visibility": st.column_config.TextColumn("Visibility", width="small"),
                        "Created": st.column_config.TextColumn("Created", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            # Growth over time
            st.markdown("### 📅 Group Growth Over Time")
            
            # This would require creation date analysis
            st.info("Group growth analytics coming soon!")
        else:
            st.info("No group data available for analytics.")
    
    with tab3:
        # Group Policies
        st.subheader("⚖️ Group Policies")
        
        # Policy settings
        with st.form("group_policies_form"):
            st.markdown("### 🛡️ Group Creation Policies")
            
            col_pol1, col_pol2 = st.columns(2)
            
            with col_pol1:
                min_members_required = st.number_input(
                    "Minimum members required for active group",
                    min_value=1,
                    value=5
                )
                
                max_groups_per_user = st.number_input(
                    "Maximum groups a user can create",
                    min_value=1,
                    value=10
                )
                
                require_description = st.checkbox(
                    "Require description for new groups",
                    value=True
                )
            
            with col_pol2:
                auto_approve_student_groups = st.checkbox(
                    "Auto-approve student-created groups",
                    value=True
                )
                
                require_admin_approval = st.checkbox(
                    "Require admin approval for all new groups",
                    value=False
                )
                
                allow_private_groups = st.checkbox(
                    "Allow private groups",
                    value=True
                )
            
            st.markdown("### 📝 Content Policies")
            
            content_moderation = st.selectbox(
                "Group content moderation level",
                ["Self-moderated", "Admin-reviewed", "Strict moderation"]
            )
            
            prohibited_categories = st.multiselect(
                "Prohibited group categories",
                ["Political", "Religious", "Commercial", "Exclusive", "Other sensitive topics"]
            )
            
            st.markdown("### 👥 Membership Policies")
            
            col_mem1, col_mem2 = st.columns(2)
            
            with col_mem1:
                max_group_members = st.number_input(
                    "Maximum members per group",
                    min_value=10,
                    value=500
                )
                
                allow_cross_role = st.checkbox(
                    "Allow mixed student-alumni groups",
                    value=True
                )
            
            with col_mem2:
                min_active_members = st.number_input(
                    "Minimum active members to avoid archiving",
                    min_value=1,
                    value=5
                )
                
                inactive_group_days = st.number_input(
                    "Days of inactivity before archiving",
                    min_value=30,
                    value=90
                )
            
            if st.form_submit_button("Save Policies", type="primary"):
                st.success("Group policies saved successfully!")
        
        # Policy enforcement
        st.markdown("---")
        st.subheader("🔍 Policy Enforcement")
        
        col_enforce1, col_enforce2, col_enforce3 = st.columns(3)
        
        with col_enforce1:
            if st.button("Scan for Violations", use_container_width=True):
                st.info("Policy violation scan coming soon!")
        
        with col_enforce2:
            if st.button("Review Flagged Groups", use_container_width=True):
                st.info("Flagged groups review coming soon!")
        
        with col_enforce3:
            if st.button("Archive Inactive Groups", use_container_width=True):
                st.info("Group archiving coming soon!")
        
        # Policy documentation
        with st.expander("📋 Policy Documentation", expanded=False):
            st.markdown("""
            ### Group Management Policies
            
            **Group Creation:**
            - All groups must have a clear purpose
            - Descriptions must be informative
            - Categories must be appropriate
            - Admins reserve right to remove inappropriate groups
            
            **Content Standards:**
            - No hate speech or discrimination
            - No harassment or bullying
            - Respect all members
            - Follow platform-wide rules
            
            **Membership Rules:**
            - Respect member privacy
            - No spamming or advertising
            - Active participation encouraged
            - Report issues to admins
            
            **Enforcement:**
            - First violation: Warning
            - Second violation: Temporary suspension
            - Repeated violations: Group removal
            - Serious violations: Immediate removal
            """)

def display_group_admin_card(group):
    """Display a group card for admin management"""
    with st.container():
        # Determine group status
        is_public = group['is_public'] == 1
        status_color = '🟢' if is_public else '🔒'
        status_text = 'Public' if is_public else 'Private'
        
        # Card header
        col_head1, col_head2 = st.columns([4, 1])
        
        with col_head1:
            st.markdown(f"### {group['name']}")
            
            # Category and status
            category = group.get('category', 'general').title()
            st.caption(f"{status_color} {status_text} • 📁 {category} • 👥 {group['member_count']} members")
        
        with col_head2:
            # Created date
            st.caption(f"📅 {group['created_at'][:10]}")
            st.caption(f"By: {group['creator_first_name']}")
        
        # Description preview
        if group.get('description'):
            preview = group['description'][:150] + "..." if len(group['description']) > 150 else group['description']
            st.markdown(f"> {preview}")
        
        # Group details
        with st.expander("📊 Group Details", expanded=False):
            col_detail1, col_detail2 = st.columns(2)
            
            with col_detail1:
                st.markdown(f"**Group ID:** `{group['id']}`")
                st.markdown(f"**Category:** {category}")
                st.markdown(f"**Visibility:** {status_text}")
                st.markdown(f"**Created:** {group['created_at'][:19]}")
            
            with col_detail2:
                st.markdown(f"**Creator:** {group['creator_first_name']} {group['creator_last_name']}")
                st.markdown(f"**Members:** {group['member_count']}")
                # Active members (placeholder)
                st.markdown(f"**Active Members:** Calculating...")
            
            # Member list
            st.markdown("### 👥 Members")
            members = get_group_members(group['id'])
            
            if members:
                # Show first 10 members
                for member in members[:10]:
                    col_mem1, col_mem2 = st.columns([3, 1])
                    with col_mem1:
                        st.markdown(f"• {member['first_name']} {member['last_name']} ({member['role'].title()})")
                    with col_mem2:
                        st.caption(member['group_role'].title())
                
                if len(members) > 10:
                    st.caption(f"... and {len(members) - 10} more members")
            else:
                st.info("No members yet")
        
        # Admin actions
        st.markdown("### ⚙️ Admin Actions")
        
        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
        
        with col_action1:
            if st.button("View Full", key=f"view_{group['id']}"):
                # Show full group details
                with st.expander("Full Group Information", expanded=True):
                    st.markdown(f"**Name:** {group['name']}")
                    st.markdown(f"**Description:** {group.get('description', 'No description')}")
                    st.markdown(f"**Category:** {category}")
                    st.markdown(f"**Visibility:** {status_text}")
                    st.markdown(f"**Created:** {group['created_at']}")
                    st.markdown(f"**Creator:** {group['creator_first_name']} {group['creator_last_name']}")
                    
                    # Member statistics
                    members = get_group_members(group['id'])
                    student_count = len([m for m in members if m['role'] == 'student'])
                    alumni_count = len([m for m in members if m['role'] == 'alumni'])
                    
                    st.markdown(f"**Total Members:** {len(members)}")
                    st.markdown(f"**Students:** {student_count}")
                    st.markdown(f"**Alumni:** {alumni_count}")
        
        with col_action2:
            if st.button("Edit", key=f"edit_{group['id']}"):
                st.info("Group editing feature coming soon!")
        
        with col_action3:
            if is_public:
                if st.button("Make Private", key=f"private_{group['id']}"):
                    st.info("Change visibility feature coming soon!")
            else:
                if st.button("Make Public", key=f"public_{group['id']}"):
                    st.info("Change visibility feature coming soon!")
        
        with col_action4:
            if st.button("Delete", key=f"delete_{group['id']}", type="secondary"):
                st.warning(f"Delete group '{group['name']}'?")
                if st.button("Confirm Delete", key=f"confirm_del_{group['id']}"):
                    st.info("Group deletion feature coming soon!")
        
        # Group activity
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            st.caption("💬 Messages: Calculating...")
        
        with col_act2:
            st.caption("📅 Last Active: Calculating...")
        
        with col_act3:
            st.caption("📈 Activity: Calculating...")
        
        st.markdown("---")
