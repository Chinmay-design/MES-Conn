import streamlit as st
from utils.database import (
    get_groups, create_group, join_group, get_group_members,
    get_group_messages, send_group_message, get_user_by_id
)

def student_groups_page(user_id):
    """Student Groups Page"""
    st.title("👥 Groups")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["My Groups", "Discover Groups", "Create Group", "Group Chat"])
    
    with tab1:
        # My Groups
        st.subheader("My Groups")
        
        groups = get_groups(user_id=user_id)
        
        if groups:
            # Filter groups by membership status
            my_groups = [g for g in groups if g.get('user_role')]
            joined_groups = [g for g in groups if not g.get('user_role') and g['is_public'] == 1]
            
            if my_groups:
                st.markdown("### 🏆 Groups I'm In")
                cols = st.columns(3)
                for idx, group in enumerate(my_groups):
                    with cols[idx % 3]:
                        display_group_card(group, user_id)
            
            if joined_groups:
                st.markdown("### 🌐 Public Groups")
                cols = st.columns(3)
                for idx, group in enumerate(joined_groups[:3]):  # Show first 3
                    with cols[idx % 3]:
                        display_group_card(group, user_id, show_join=True)
                
                if len(joined_groups) > 3:
                    with st.expander("Show more public groups"):
                        more_cols = st.columns(3)
                        for idx, group in enumerate(joined_groups[3:6]):
                            with more_cols[idx % 3]:
                                display_group_card(group, user_id, show_join=True)
        else:
            st.info("You haven't joined any groups yet.")
    
    with tab2:
        # Discover Groups
        st.subheader("Discover Groups")
        
        # Search and filters
        col_search1, col_search2 = st.columns(2)
        
        with col_search1:
            search_term = st.text_input("🔍 Search groups")
        
        with col_search2:
            category_filter = st.selectbox(
                "Filter by category",
                ["All", "Study", "Sports", "Cultural", "Technical", "Hobbies", "Other"]
            )
        
        # Get all groups
        all_groups = get_groups()
        
        # Apply filters
        filtered_groups = all_groups
        if search_term:
            filtered_groups = [
                g for g in filtered_groups 
                if search_term.lower() in g['name'].lower()
                or search_term.lower() in g.get('description', '').lower()
            ]
        
        if category_filter != "All":
            filtered_groups = [g for g in filtered_groups if g.get('category') == category_filter.lower()]
        
        # Display groups
        if filtered_groups:
            st.markdown(f"Found **{len(filtered_groups)}** groups")
            
            cols = st.columns(3)
            for idx, group in enumerate(filtered_groups[:9]):  # Show max 9
                with cols[idx % 3]:
                    display_group_card(group, user_id, show_join=True)
            
            if len(filtered_groups) > 9:
                if st.button("Load More", type="secondary"):
                    st.info("Pagination feature coming soon!")
        else:
            st.info("No groups found with the current filters.")
    
    with tab3:
        # Create Group
        st.subheader("Create New Group")
        
        with st.form("create_group_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                group_name = st.text_input("Group Name *", placeholder="e.g., CS Study Group 2024")
                category = st.selectbox(
                    "Category *",
                    ["study", "sports", "cultural", "technical", "hobbies", "other"]
                )
                is_public = st.radio(
                    "Visibility *",
                    ["Public (Anyone can join)", "Private (Invite only)"],
                    index=0
                )
            
            with col2:
                description = st.text_area(
                    "Description *",
                    placeholder="Describe your group's purpose, rules, and activities...",
                    height=150
                )
                
                # Optional fields
                cover_pic = st.file_uploader("Cover Picture", type=['jpg', 'jpeg', 'png'])
            
            submit = st.form_submit_button("Create Group", type="primary")
            
            if submit:
                if not all([group_name, description]):
                    st.error("Please fill all required fields (*)")
                else:
                    group_data = {
                        'is_public': 1 if is_public == "Public (Anyone can join)" else 0,
                        'category': category
                    }
                    
                    if cover_pic:
                        # Handle cover picture upload
                        import base64
                        image_bytes = cover_pic.read()
                        b64_string = base64.b64encode(image_bytes).decode()
                        group_data['cover_pic'] = f"data:image/jpeg;base64,{b64_string}"
                    
                    group_id = create_group(
                        name=group_name,
                        description=description,
                        created_by=user_id,
                        **group_data
                    )
                    
                    if group_id:
                        st.success(f"Group '{group_name}' created successfully!")
                        st.balloons()
                        
                        # Show next steps
                        with st.expander("Next Steps", expanded=True):
                            st.markdown("""
                            ### 🎉 Your group has been created!
                            
                            **Here's what you can do next:**
                            
                            1. **Invite Members** - Share the group link with friends
                            2. **Set Group Rules** - Establish guidelines for members
                            3. **Post Announcements** - Share important updates
                            4. **Start Discussions** - Engage members in conversations
                            5. **Schedule Events** - Plan group activities
                            
                            **Group Link:** `mes-connect.com/groups/{group_id}`
                            """)
                            
                            col_next1, col_next2 = st.columns(2)
                            with col_next1:
                                if st.button("Go to Group", type="primary"):
                                    st.session_state.current_group = group_id
                                    st.rerun()
                            with col_next2:
                                if st.button("Invite Friends"):
                                    st.info("Invite feature coming soon!")
                    else:
                        st.error("Failed to create group")
    
    with tab4:
        # Group Chat
        st.subheader("Group Chat")
        
        # Get user's groups
        user_groups = [g for g in get_groups(user_id=user_id) if g.get('user_role')]
        
        if user_groups:
            # Group selection
            selected_group = st.selectbox(
                "Select a group to chat",
                options=[f"{g['name']} ({g['member_count']} members)" for g in user_groups],
                format_func=lambda x: x
            )
            
            # Find selected group
            group_index = [f"{g['name']} ({g['member_count']} members)" for g in user_groups].index(selected_group)
            selected_group_data = user_groups[group_index]
            
            # Display group chat
            display_group_chat(selected_group_data, user_id)
        else:
            st.info("Join a group to start chatting!")
            
            # Suggest groups to join
            st.subheader("Suggested Groups")
            suggested_groups = get_groups()[:3]
            
            if suggested_groups:
                cols = st.columns(3)
                for idx, group in enumerate(suggested_groups):
                    with cols[idx % 3]:
                        display_group_card(group, user_id, show_join=True)

def display_group_card(group, user_id, show_join=False):
    """Display a group card"""
    with st.container():
        st.markdown(f"<div class='group-card'>", unsafe_allow_html=True)
        
        # Group header
        st.markdown(f"### {group['name']}")
        
        # Category badge
        category_colors = {
            'study': '🔵',
            'sports': '🟢',
            'cultural': '🟣',
            'technical': '🟠',
            'hobbies': '🟡',
            'other': '⚫'
        }
        category_icon = category_colors.get(group.get('category', 'other'), '⚫')
        st.caption(f"{category_icon} {group.get('category', 'general').title()} • 👥 {group['member_count']} members")
        
        # Description preview
        if group.get('description'):
            st.markdown(f"> {group['description'][:100]}...")
        
        # Group info
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.caption(f"Created by: {group['creator_first_name']}")
        with col_info2:
            visibility = "🌐 Public" if group['is_public'] == 1 else "🔒 Private"
            st.caption(visibility)
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if group.get('user_role'):
                st.success(f"✅ {group['user_role'].title()}")
            elif show_join:
                if st.button("Join", key=f"join_{group['id']}"):
                    if join_group(group['id'], user_id):
                        st.success("Joined successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to join group")
        
        with col_btn2:
            if st.button("View", key=f"view_{group['id']}"):
                with st.expander("Group Details", expanded=True):
                    st.markdown(f"**Description:** {group.get('description', 'No description')}")
                    st.markdown(f"**Created:** {group['created_at'][:10]}")
                    st.markdown(f"**Category:** {group.get('category', 'general').title()}")
                    st.markdown(f"**Visibility:** {'Public' if group['is_public'] == 1 else 'Private'}")
                    
                    # Show members count
                    members = get_group_members(group['id'])
                    st.markdown(f"**Members:** {len(members)}")
                    
                    if members:
                        with st.expander("View Members"):
                            for member in members[:10]:  # Show first 10
                                st.markdown(f"• {member['first_name']} {member['last_name']} ({member['group_role']})")
                    
                    if not group.get('user_role') and group['is_public'] == 1:
                        if st.button("Join Group", key=f"join_exp_{group['id']}"):
                            if join_group(group['id'], user_id):
                                st.success("Joined successfully!")
                                st.rerun()
        
        with col_btn3:
            if group.get('user_role'):
                if st.button("Chat", key=f"chat_{group['id']}"):
                    st.session_state.current_group = group['id']
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_group_chat(group, user_id):
    """Display group chat interface"""
    # Chat header
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.markdown(f"### 💬 {group['name']}")
        st.caption(f"{group['member_count']} members • {group.get('category', 'general').title()}")
    with col_header2:
        if st.button("Back", type="secondary"):
            st.session_state.current_group = None
            st.rerun()
    
    st.markdown("---")
    
    # Chat messages area
    chat_container = st.container(height=400)
    
    with chat_container:
        # Get group messages
        messages = get_group_messages(group['id'], limit=50)
        
        if messages:
            for msg in messages:
                # Display message
                col_msg1, col_msg2 = st.columns([1, 6])
                
                with col_msg1:
                    # Sender avatar
                    if msg.get('profile_pic'):
                        st.image(msg['profile_pic'], width=40)
                    else:
                        st.image("https://via.placeholder.com/40", width=40)
                
                with col_msg2:
                    # Message content
                    sender_name = f"{msg['first_name']} {msg['last_name']}"
                    if msg['sender_id'] == user_id:
                        sender_name = "You"
                    
                    st.markdown(f"**{sender_name}** ({msg['role'].title()})")
                    st.markdown(msg['message'])
                    st.caption(f"{msg['created_at'][11:16]}")
                    
                    st.markdown("---")
        else:
            st.info("No messages yet. Start the conversation!")
    
    # Message input area
    st.markdown("---")
    
    with st.form("group_message_form", clear_on_submit=True):
        col_input1, col_input2 = st.columns([4, 1])
        
        with col_input1:
            message = st.text_input(
                f"Message {group['name']}...",
                key=f"group_msg_{group['id']}",
                label_visibility="collapsed",
                placeholder="Type your message here..."
            )
        
        with col_input2:
            send_btn = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        if send_btn and message:
            if send_group_message(group['id'], user_id, message):
                st.rerun()
            else:
                st.error("Failed to send message")
    
    # Group management (for admins/moderators)
    user_role = None
    for g in get_groups(user_id=user_id):
        if g['id'] == group['id']:
            user_role = g.get('user_role')
            break
    
    if user_role in ['admin', 'moderator']:
        st.markdown("---")
        st.subheader("Group Management")
        
        col_manage1, col_manage2, col_manage3 = st.columns(3)
        
        with col_manage1:
            if st.button("👥 Manage Members", use_container_width=True):
                # Show members management
                with st.expander("Group Members", expanded=True):
                    members = get_group_members(group['id'])
                    
                    for member in members:
                        col_mem1, col_mem2, col_mem3 = st.columns([3, 2, 1])
                        
                        with col_mem1:
                            st.markdown(f"**{member['first_name']} {member['last_name']}**")
                            st.caption(member['email'])
                        
                        with col_mem2:
                            st.markdown(f"Role: **{member['group_role']}**")
                        
                        with col_mem3:
                            if user_role == 'admin' and member['group_role'] != 'admin':
                                if st.button("Remove", key=f"remove_{member['id']}"):
                                    st.info("Remove member feature coming soon!")
        
        with col_manage2:
            if st.button("📢 Post Announcement", use_container_width=True):
                st.info("Announcement feature coming soon!")
        
        with col_manage3:
            if st.button("⚙️ Group Settings", use_container_width=True):
                st.info("Group settings feature coming soon!")
