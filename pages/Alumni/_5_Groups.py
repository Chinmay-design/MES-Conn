import streamlit as st
from utils.database import (
    get_groups, create_group, join_group, get_group_members,
    get_group_messages, send_group_message, get_user_by_id
)

def alumni_groups_page(user_id):
    """Alumni Groups Page"""
    st.title("👥 Alumni Groups")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "My Groups", "Industry Groups", "Create Group", "Group Chat"
    ])
    
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
                        display_alumni_group_card(group, user_id)
            
            if joined_groups:
                st.markdown("### 🌐 Public Groups")
                cols = st.columns(3)
                for idx, group in enumerate(joined_groups[:3]):
                    with cols[idx % 3]:
                        display_alumni_group_card(group, user_id, show_join=True)
        else:
            st.info("You haven't joined any groups yet.")
    
    with tab2:
        # Industry Groups
        st.subheader("🏢 Industry Groups")
        
        # Industry categories
        industries = [
            ("Technology", "💻", "Tech companies, startups, software development"),
            ("Finance", "🏦", "Banking, investment, fintech, accounting"),
            ("Healthcare", "🏥", "Medical, pharma, healthcare services"),
            ("Manufacturing", "🏭", "Industrial, automotive, consumer goods"),
            ("Education", "🎓", "Academia, teaching, edtech, research"),
            ("Consulting", "💼", "Management, strategy, business consulting"),
            ("Entrepreneurship", "🚀", "Startups, business owners, investors"),
            ("Research", "🔬", "R&D, scientific research, innovation")
        ]
        
        # Display industry groups
        cols = st.columns(4)
        for idx, (industry, icon, description) in enumerate(industries):
            with cols[idx % 4]:
                with st.container():
                    st.markdown(f"### {icon} {industry}")
                    st.caption(description)
                    
                    # Get groups in this category
                    industry_groups = [g for g in get_groups() if g.get('category') == industry.lower()]
                    
                    if industry_groups:
                        member_count = sum(g['member_count'] for g in industry_groups)
                        st.metric("Total Members", member_count)
                        
                        # Show top groups
                        with st.expander(f"Groups ({len(industry_groups)})"):
                            for group in industry_groups[:3]:
                                st.markdown(f"**{group['name']}**")
                                st.caption(f"👥 {group['member_count']} members")
                                
                                if st.button(f"Join {industry}", key=f"join_ind_{group['id']}"):
                                    if join_group(group['id'], user_id):
                                        st.success(f"Joined {group['name']}!")
                                        st.rerun()
                    else:
                        st.info("No groups yet")
                        
                        if st.button(f"Create {industry} Group", key=f"create_ind_{idx}"):
                            st.session_state.current_page = "Alumni/Groups"
                            st.rerun()
        
        # Alumni Association Groups
        st.markdown("---")
        st.subheader("🎓 Alumni Association")
        
        assoc_groups = [
            ("Class of 2020", "👨‍🎓", "Graduates from 2020"),
            ("Class of 2015", "👨‍🎓", "5-year reunion group"),
            ("Class of 2010", "👨‍🎓", "10-year reunion group"),
            ("Department Alumni", "🎓", "All alumni from your department")
        ]
        
        cols = st.columns(4)
        for idx, (group_name, icon, description) in enumerate(assoc_groups):
            with cols[idx % 4]:
                with st.container():
                    st.markdown(f"### {icon} {group_name}")
                    st.caption(description)
                    
                    member_count = 0  # Would need to calculate
                    st.metric("Members", member_count)
                    
                    if st.button(f"Join {group_name}", key=f"join_assoc_{idx}"):
                        st.info(f"Joining {group_name}...")
    
    with tab3:
        # Create Group
        st.subheader("Create Professional Group")
        
        with st.form("create_alumni_group_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                group_name = st.text_input("Group Name *", placeholder="e.g., MES Tech Alumni Network")
                category = st.selectbox(
                    "Category *",
                    ["technology", "finance", "healthcare", "manufacturing", 
                     "education", "consulting", "entrepreneurship", "research", 
                     "alumni", "professional", "other"]
                )
                group_type = st.radio(
                    "Group Type *",
                    ["Professional Network", "Industry Discussion", "Mentorship", "Job Board", "Social"]
                )
                is_public = st.radio(
                    "Visibility *",
                    ["Public (Anyone can join)", "Private (Approval required)"],
                    index=0
                )
            
            with col2:
                description = st.text_area(
                    "Description *",
                    placeholder="Describe your group's purpose, rules, and professional focus...",
                    height=150
                )
                
                # Professional focus
                focus_areas = st.multiselect(
                    "Focus Areas",
                    ["Networking", "Job Opportunities", "Mentorship", "Industry News", 
                     "Skill Development", "Career Growth", "Business Opportunities", 
                     "Professional Development"]
                )
                
                # Target audience
                target_audience = st.multiselect(
                    "Target Audience",
                    ["All Alumni", "Recent Graduates", "Senior Professionals", 
                     "Entrepreneurs", "Industry Specific", "Location Based"]
                )
            
            # Group rules and guidelines
            with st.expander("Group Rules & Guidelines (Optional)"):
                rules = st.text_area(
                    "Establish group rules",
                    placeholder="e.g., Be professional, no spam, respect all members...",
                    height=100
                )
            
            submit = st.form_submit_button("Create Professional Group", type="primary")
            
            if submit:
                if not all([group_name, description]):
                    st.error("Please fill all required fields (*)")
                else:
                    group_data = {
                        'is_public': 1 if is_public == "Public (Anyone can join)" else 0,
                        'category': category,
                        'description': description + f"\n\nType: {group_type}\nFocus: {', '.join(focus_areas)}\nAudience: {', '.join(target_audience)}"
                    }
                    
                    if rules:
                        group_data['description'] += f"\n\nRules:\n{rules}"
                    
                    group_id = create_group(
                        name=group_name,
                        description=group_data['description'],
                        created_by=user_id,
                        **group_data
                    )
                    
                    if group_id:
                        st.success(f"🎉 Professional group '{group_name}' created successfully!")
                        st.balloons()
                        
                        with st.expander("Next Steps for Professional Groups", expanded=True):
                            st.markdown(f"""
                            ### 🎯 Your professional group is ready!
                            
                            **Group ID:** `{group_id}`
                            **Share Link:** `mes-connect.com/groups/{group_id}`
                            
                            **Professional Group Management:**
                            
                            1. **📢 Invite Members** - Share with relevant professionals
                            2. **🏢 Set Professional Tone** - Establish clear guidelines
                            3. **💼 Post Opportunities** - Share jobs and internships
                            4. **🎤 Schedule Events** - Organize webinars and meetups
                            5. **📚 Share Resources** - Post industry articles and guides
                            
                            **Best Practices:**
                            - Maintain professional decorum
                            - Share valuable industry insights
                            - Foster meaningful connections
                            - Moderate discussions effectively
                            - Encourage member participation
                            """)
                            
                            col_next1, col_next2 = st.columns(2)
                            with col_next1:
                                if st.button("Go to Group", type="primary"):
                                    st.session_state.current_group = group_id
                                    st.rerun()
                            with col_next2:
                                if st.button("Invite Professionals"):
                                    st.info("Professional invitation feature coming soon!")
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
            display_alumni_group_chat(selected_group_data, user_id)
        else:
            st.info("Join a group to start chatting!")
            
            # Suggest professional groups
            st.subheader("Suggested Professional Groups")
            suggested_groups = get_groups()[:3]
            
            if suggested_groups:
                cols = st.columns(3)
                for idx, group in enumerate(suggested_groups):
                    with cols[idx % 3]:
                        display_alumni_group_card(group, user_id, show_join=True)

def display_alumni_group_card(group, user_id, show_join=False):
    """Display an alumni group card"""
    with st.container():
        st.markdown(f"<div class='group-card'>", unsafe_allow_html=True)
        
        # Group header
        st.markdown(f"### {group['name']}")
        
        # Category and type
        category_icons = {
            'technology': '💻',
            'finance': '🏦',
            'healthcare': '🏥',
            'manufacturing': '🏭',
            'education': '🎓',
            'consulting': '💼',
            'entrepreneurship': '🚀',
            'research': '🔬',
            'alumni': '👨‍🎓',
            'professional': '💼',
            'other': '👥'
        }
        category_icon = category_icons.get(group.get('category', 'other'), '👥')
        st.caption(f"{category_icon} {group.get('category', 'professional').title()} • 👥 {group['member_count']} members")
        
        # Description preview
        if group.get('description'):
            st.markdown(f"> {group['description'][:100]}...")
        
        # Professional info
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
                if st.button("Join", key=f"alum_join_{group['id']}"):
                    if join_group(group['id'], user_id):
                        st.success("Joined successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to join group")
        
        with col_btn2:
            if st.button("View", key=f"alum_view_{group['id']}"):
                with st.expander("Group Details", expanded=True):
                    st.markdown(f"**Description:** {group.get('description', 'No description')}")
                    
                    # Show professional focus if available
                    if "Type:" in group.get('description', ''):
                        desc_lines = group['description'].split('\n')
                        for line in desc_lines:
                            if line.startswith(('Type:', 'Focus:', 'Audience:', 'Rules:')):
                                st.markdown(f"**{line}**")
                    
                    st.markdown(f"**Created:** {group['created_at'][:10]}")
                    st.markdown(f"**Category:** {group.get('category', 'professional').title()}")
                    st.markdown(f"**Visibility:** {'Public' if group['is_public'] == 1 else 'Private'}")
                    
                    # Show members
                    members = get_group_members(group['id'])
                    st.markdown(f"**Members:** {len(members)}")
                    
                    if members:
                        with st.expander("View Professional Members"):
                            for member in members[:10]:
                                role_badge = "👨‍🎓" if member['role'] == 'alumni' else "👨‍🎓"
                                st.markdown(f"• {role_badge} {member['first_name']} {member['last_name']} - {member.get('current_position', '')}")
                    
                    if not group.get('user_role') and group['is_public'] == 1:
                        if st.button("Join Professional Group", key=f"join_exp_{group['id']}"):
                            if join_group(group['id'], user_id):
                                st.success("Joined successfully!")
                                st.rerun()
        
        with col_btn3:
            if group.get('user_role'):
                if st.button("Chat", key=f"alum_chat_{group['id']}"):
                    st.session_state.current_group = group['id']
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def display_alumni_group_chat(group, user_id):
    """Display alumni group chat interface"""
    # Chat header
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.markdown(f"### 💬 {group['name']}")
        st.caption(f"{group['member_count']} members • {group.get('category', 'professional').title()} Group")
    with col_header2:
        if st.button("Back", type="secondary"):
            st.session_state.current_group = None
            st.rerun()
    
    st.markdown("---")
    
    # Professional group info
    with st.expander("📋 Group Information", expanded=False):
        st.markdown(f"**Description:** {group.get('description', 'No description')}")
        
        # Show members
        members = get_group_members(group['id'])
        alumni_members = [m for m in members if m['role'] == 'alumni']
        student_members = [m for m in members if m['role'] == 'student']
        
        col_mem1, col_mem2 = st.columns(2)
        with col_mem1:
            st.markdown(f"**Alumni:** {len(alumni_members)}")
        with col_mem2:
            st.markdown(f"**Students:** {len(student_members)}")
        
        # Professional opportunities section
        st.markdown("### 💼 Professional Opportunities")
        
        col_opp1, col_opp2, col_opp3 = st.columns(3)
        with col_opp1:
            if st.button("Post Job", use_container_width=True):
                st.info("Job posting feature coming soon!")
        with col_opp2:
            if st.button("Share Event", use_container_width=True):
                st.info("Event sharing feature coming soon!")
        with col_opp3:
            if st.button("Ask for Advice", use_container_width=True):
                st.info("Advice request feature coming soon!")
    
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
                    # Sender info
                    if msg.get('profile_pic'):
                        st.image(msg['profile_pic'], width=40)
                    else:
                        st.image("https://via.placeholder.com/40", width=40)
                
                with col_msg2:
                    # Message content with professional context
                    sender_name = f"{msg['first_name']} {msg['last_name']}"
                    if msg['sender_id'] == user_id:
                        sender_name = "You"
                    
                    # Add professional badge for alumni
                    role_badge = "👨‍🎓" if msg['role'] == 'alumni' else "👨‍🎓"
                    
                    st.markdown(f"**{role_badge} {sender_name}** ({msg['role'].title()})")
                    st.markdown(msg['message'])
                    
                    # Professional tags if message contains opportunities
                    if any(keyword in msg['message'].lower() for keyword in ['job', 'hire', 'opportunity', 'internship', 'mentor']):
                        st.caption("💼 Professional Opportunity")
                    
                    st.caption(f"{msg['created_at'][11:16]}")
                    
                    st.markdown("---")
        else:
            st.info("No messages yet. Start the professional conversation!")
    
    # Message input area
    st.markdown("---")
    
    with st.form("alumni_group_message_form", clear_on_submit=True):
        col_input1, col_input2 = st.columns([4, 1])
        
        with col_input1:
            message = st.text_input(
                f"Message {group['name']}...",
                key=f"alum_group_msg_{group['id']}",
                label_visibility="collapsed",
                placeholder="Type your message here... (Use #opportunity for job posts)"
            )
        
        with col_input2:
            send_btn = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        if send_btn and message:
            if send_group_message(group['id'], user_id, message):
                st.rerun()
            else:
                st.error("Failed to send message")
    
    # Professional group management
    user_role = None
    for g in get_groups(user_id=user_id):
        if g['id'] == group['id']:
            user_role = g.get('user_role')
            break
    
    if user_role in ['admin', 'moderator']:
        st.markdown("---")
        st.subheader("Professional Group Management")
        
        col_manage1, col_manage2, col_manage3 = st.columns(3)
        
        with col_manage1:
            if st.button("👥 Manage Members", use_container_width=True):
                with st.expander("Member Management", expanded=True):
                    members = get_group_members(group['id'])
                    
                    for member in members:
                        col_mem1, col_mem2, col_mem3, col_mem4 = st.columns([3, 2, 2, 1])
                        
                        with col_mem1:
                            st.markdown(f"**{member['first_name']} {member['last_name']}**")
                            st.caption(f"{member['role'].title()} • {member.get('current_position', '')}")
                        
                        with col_mem2:
                            st.markdown(f"Role: **{member['group_role']}**")
                        
                        with col_mem3:
                            st.caption(f"Joined: {member['joined_at'][:10]}")
                        
                        with col_mem4:
                            if user_role == 'admin' and member['group_role'] != 'admin':
                                if st.button("Remove", key=f"alum_remove_{member['id']}"):
                                    st.info("Remove member feature coming soon!")
        
        with col_manage2:
            if st.button("📢 Post Announcement", use_container_width=True):
                with st.form("professional_announcement_form"):
                    title = st.text_input("Announcement Title")
                    content = st.text_area("Announcement Content")
                    
                    if st.form_submit_button("Post Announcement", type="primary"):
                        # Send as message
                        announcement_msg = f"📢 **{title}**\n\n{content}"
                        if send_group_message(group['id'], user_id, announcement_msg):
                            st.success("Announcement posted!")
                            st.rerun()
        
        with col_manage3:
            if st.button("📅 Schedule Event", use_container_width=True):
                st.info("Event scheduling feature coming soon!")
