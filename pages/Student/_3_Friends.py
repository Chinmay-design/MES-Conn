import streamlit as st
from utils.database import (
    get_friends, get_pending_friend_requests,
    accept_friend_request, reject_friend_request,
    add_friend_request, get_all_users,
    get_user_by_id, remove_friend
)

def student_friends_page(user_id):
    """Student Friends Management Page"""
    st.title("👥 Friends Management")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["My Friends", "Friend Requests", "Find Friends", "Blocked Users"])
    
    with tab1:
        # My Friends
        st.subheader("My Friends")
        
        friends = get_friends(user_id, status='accepted')
        
        if friends:
            search_term = st.text_input("🔍 Search friends...")
            
            # Filter friends based on search
            filtered_friends = friends
            if search_term:
                filtered_friends = [
                    f for f in friends 
                    if search_term.lower() in f['first_name'].lower() 
                    or search_term.lower() in f['last_name'].lower()
                    or search_term.lower() in f.get('department', '').lower()
                ]
            
            if filtered_friends:
                cols = st.columns(4)
                for idx, friend in enumerate(filtered_friends):
                    with cols[idx % 4]:
                        with st.container():
                            # Friend card
                            st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                            
                            if friend.get('profile_pic'):
                                st.image(friend['profile_pic'], width=80)
                            else:
                                st.image("https://via.placeholder.com/80", width=80)
                            
                            st.markdown(f"**{friend['first_name']} {friend['last_name']}**")
                            st.caption(friend.get('department', ''))
                            
                            if friend.get('current_position'):
                                st.caption(f"💼 {friend['current_position']}")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("💬", key=f"chat_f_{friend['id']}", help="Chat"):
                                    st.session_state.chat_with = friend['id']
                                    st.session_state.current_page = "Student/Chat"
                                    st.rerun()
                            with col_btn2:
                                if st.button("👁️", key=f"view_f_{friend['id']}", help="View Profile"):
                                    with st.expander("Friend Profile", expanded=True):
                                        friend_details = get_user_by_id(friend['id'])
                                        if friend_details:
                                            st.write(f"**Email:** {friend_details['email']}")
                                            st.write(f"**Phone:** {friend_details.get('phone', 'Not provided')}")
                                            st.write(f"**Joined:** {friend_details['created_at'][:10]}")
                                            if friend_details.get('skills'):
                                                st.write(f"**Skills:** {friend_details['skills']}")
                                            if friend_details.get('about'):
                                                st.write(f"**About:** {friend_details['about']}")
                            
                            if st.button("Remove", key=f"remove_{friend['id']}", type="secondary"):
                                if remove_friend(user_id, friend['id']):
                                    st.success("Friend removed")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove friend")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.markdown("---")
            else:
                if search_term:
                    st.warning("No friends match your search")
                else:
                    st.info("You haven't added any friends yet.")
        else:
            st.info("You haven't added any friends yet.")
    
    with tab2:
        # Friend Requests
        st.subheader("Friend Requests")
        
        # Pending requests received
        st.markdown("### 📥 Received Requests")
        pending_requests = get_pending_friend_requests(user_id)
        
        if pending_requests:
            for request in pending_requests:
                with st.container():
                    col_r1, col_r2, col_r3, col_r4 = st.columns([3, 1, 1, 1])
                    
                    with col_r1:
                        st.markdown(f"**{request['first_name']} {request['last_name']}**")
                        st.caption(f"{request.get('department', '')} • {request.get('role', '').title()}")
                        if request.get('current_position'):
                            st.caption(f"💼 {request['current_position']} at {request.get('company', '')}")
                        st.caption(f"Sent on {request['created_at'][:10]}")
                    
                    with col_r2:
                        if st.button("Accept", key=f"accept_{request['request_id']}", type="primary"):
                            if accept_friend_request(request['request_id'], user_id):
                                st.success("Friend request accepted!")
                                st.rerun()
                    
                    with col_r3:
                        if st.button("Reject", key=f"reject_{request['request_id']}"):
                            if reject_friend_request(request['request_id'], user_id):
                                st.success("Friend request rejected")
                                st.rerun()
                    
                    with col_r4:
                        if st.button("View", key=f"view_req_{request['user_id']}"):
                            with st.expander("User Profile"):
                                user_details = get_user_by_id(request['user_id'])
                                if user_details:
                                    st.write(f"**Email:** {user_details['email']}")
                                    st.write(f"**Department:** {user_details.get('department', '')}")
                                    st.write(f"**Skills:** {user_details.get('skills', 'Not specified')}")
                                    st.write(f"**About:** {user_details.get('about', 'Not specified')}")
                    
                    st.markdown("---")
        else:
            st.info("No pending friend requests.")
        
        # Sent requests (would need additional function)
        st.markdown("### 📤 Sent Requests")
        st.info("Feature coming soon!")
    
    with tab3:
        # Find Friends
        st.subheader("Find Friends")
        
        # Search and filters
        col_search1, col_search2, col_search3 = st.columns(3)
        
        with col_search1:
            search_name = st.text_input("Search by name")
        
        with col_search2:
            department_filter = st.selectbox(
                "Filter by department",
                ["All", "Computer Science", "Electronics & Communication", "Mechanical", 
                 "Civil", "Electrical", "Information Technology", "Chemical", 
                 "Biotechnology", "Aerospace", "Other"]
            )
        
        with col_search3:
            year_filter = st.selectbox(
                "Filter by year",
                ["All", "1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"]
            )
        
        # Get all users (excluding current user and existing friends)
        all_users = get_all_users(role='student', exclude_id=user_id)
        friends = get_friends(user_id, status='accepted')
        friend_ids = [f['id'] for f in friends]
        
        # Filter out existing friends
        potential_friends = [u for u in all_users if u['id'] not in friend_ids]
        
        # Apply filters
        if search_name:
            potential_friends = [
                u for u in potential_friends 
                if search_name.lower() in u['first_name'].lower() 
                or search_name.lower() in u['last_name'].lower()
            ]
        
        if department_filter != "All":
            potential_friends = [u for u in potential_friends if u.get('department') == department_filter]
        
        if year_filter != "All":
            potential_friends = [u for u in potential_friends if u.get('year') == year_filter]
        
        # Display potential friends
        if potential_friends:
            st.markdown(f"Found **{len(potential_friends)}** potential friends")
            
            cols = st.columns(3)
            for idx, user in enumerate(potential_friends[:9]):  # Show max 9
                with cols[idx % 3]:
                    with st.container():
                        # User card
                        st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                        
                        if user.get('profile_pic'):
                            st.image(user['profile_pic'], width=80)
                        else:
                            st.image("https://via.placeholder.com/80", width=80)
                        
                        st.markdown(f"**{user['first_name']} {user['last_name']}**")
                        st.caption(user.get('department', ''))
                        st.caption(user.get('year', ''))
                        
                        if user.get('skills'):
                            skills_preview = ', '.join(user['skills'].split(',')[:2])
                            st.caption(f"🛠️ {skills_preview}")
                        
                        if st.button("Add Friend", key=f"add_pot_{user['id']}", type="primary"):
                            success, msg = add_friend_request(user_id, user['id'])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        
                        if st.button("View Profile", key=f"view_pot_{user['id']}"):
                            with st.expander("User Profile", expanded=True):
                                user_details = get_user_by_id(user['id'])
                                if user_details:
                                    st.write(f"**Email:** {user_details['email']}")
                                    st.write(f"**Phone:** {user_details.get('phone', 'Not provided')}")
                                    st.write(f"**Skills:** {user_details.get('skills', 'Not specified')}")
                                    st.write(f"**About:** {user_details.get('about', 'Not specified')}")
                                    if st.button("Add Friend from Profile", key=f"add_from_profile_{user['id']}"):
                                        success, msg = add_friend_request(user_id, user['id'])
                                        if success:
                                            st.success(msg)
                                            st.rerun()
                                        else:
                                            st.error(msg)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("---")
            
            # Show more button if there are more users
            if len(potential_friends) > 9:
                if st.button("Load More", type="secondary"):
                    st.info("Pagination feature coming soon!")
        else:
            st.info("No potential friends found with the current filters.")
    
    with tab4:
        # Blocked Users
        st.subheader("Blocked Users")
        st.info("Blocked users feature coming soon!")
        
        # This would require adding a 'blocked' status to friends table
        # and implementing block/unblock functionality
