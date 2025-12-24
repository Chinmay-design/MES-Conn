import streamlit as st
import time
from datetime import datetime
from utils.database import (
    get_conversations, get_chat_messages, send_message,
    get_user_by_id, get_friends
)

def student_chat_page(user_id):
    """Student Chat Page"""
    st.title("💬 Chat")
    
    # Initialize session state for chat
    if 'chat_with' not in st.session_state:
        st.session_state.chat_with = None
    if 'message_input' not in st.session_state:
        st.session_state.message_input = ""
    if 'refresh_chat' not in st.session_state:
        st.session_state.refresh_chat = False
    
    # Get conversations and friends
    conversations = get_conversations(user_id)
    friends = get_friends(user_id, status='accepted')
    
    # Create two columns: conversations list and chat area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Conversations list
        st.subheader("Conversations")
        
        # New message button
        if st.button("✏️ New Message", use_container_width=True):
            st.session_state.chat_with = None
            st.rerun()
        
        st.markdown("---")
        
        # List conversations
        if conversations:
            for conv in conversations:
                is_active = st.session_state.chat_with == conv['user_id']
                
                # Create a container for each conversation
                with st.container():
                    col_conv1, col_conv2 = st.columns([3, 1])
                    
                    with col_conv1:
                        # Display conversation info
                        display_name = f"{conv['first_name']} {conv['last_name']}"
                        if conv.get('unread_count', 0) > 0:
                            display_name = f"**{display_name}** 🔔"
                        
                        if st.button(
                            display_name,
                            key=f"conv_{conv['user_id']}",
                            use_container_width=True,
                            type="primary" if is_active else "secondary"
                        ):
                            st.session_state.chat_with = conv['user_id']
                            st.session_state.refresh_chat = True
                            st.rerun()
                        
                        # Last message preview
                        if conv.get('last_message'):
                            preview = conv['last_message'][:30] + "..." if len(conv['last_message']) > 30 else conv['last_message']
                            st.caption(preview)
                    
                    with col_conv2:
                        # Unread count badge
                        if conv.get('unread_count', 0) > 0:
                            st.markdown(f"<div style='background-color: #EF4444; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;'>{conv['unread_count']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("---")
        else:
            st.info("No conversations yet.")
        
        # Friends list for starting new chats
        st.subheader("Friends")
        if friends:
            for friend in friends[:5]:  # Show first 5 friends
                if st.button(
                    f"💬 {friend['first_name']} {friend['last_name']}",
                    key=f"friend_chat_{friend['id']}",
                    use_container_width=True
                ):
                    st.session_state.chat_with = friend['id']
                    st.rerun()
            
            if len(friends) > 5:
                with st.expander("Show all friends"):
                    for friend in friends[5:]:
                        if st.button(
                            f"💬 {friend['first_name']} {friend['last_name']}",
                            key=f"friend_chat_all_{friend['id']}",
                            use_container_width=True
                        ):
                            st.session_state.chat_with = friend['id']
                            st.rerun()
        else:
            st.info("Add friends to start chatting")
    
    with col2:
        # Chat area
        if st.session_state.chat_with:
            # Get user info
            other_user = get_user_by_id(st.session_state.chat_with)
            
            if other_user:
                # Chat header
                col_header1, col_header2 = st.columns([4, 1])
                with col_header1:
                    st.markdown(f"### 💬 Chat with {other_user['first_name']} {other_user['last_name']}")
                    st.caption(f"{other_user.get('department', '')} • {other_user.get('role', '').title()}")
                with col_header2:
                    if st.button("Back", type="secondary"):
                        st.session_state.chat_with = None
                        st.rerun()
                
                st.markdown("---")
                
                # Chat messages area
                chat_container = st.container(height=400)
                
                with chat_container:
                    # Get and display messages
                    messages = get_chat_messages(user_id, st.session_state.chat_with, limit=50)
                    
                    if messages:
                        for msg in messages:
                            # Determine message alignment
                            is_sent = msg['sender_id'] == user_id
                            
                            # Create message bubble
                            if is_sent:
                                message_class = "message-sent"
                                align = "right"
                            else:
                                message_class = "message-received"
                                align = "left"
                            
                            # Display message
                            col_msg1, col_msg2, col_msg3 = st.columns([1, 6, 1])
                            
                            if is_sent:
                                with col_msg3:
                                    st.markdown(f"<div class='message-bubble {message_class}' style='text-align: {align};'>{msg['message']}</div>", unsafe_allow_html=True)
                                    st.caption(f"{msg['created_at'][11:16]} • {'✓✓' if msg['is_read'] else '✓'}")
                            else:
                                with col_msg2:
                                    st.markdown(f"<div class='message-bubble {message_class}' style='text-align: {align};'>{msg['message']}</div>", unsafe_allow_html=True)
                                    st.caption(f"{msg['created_at'][11:16]}")
                    
                    else:
                        st.info("No messages yet. Start the conversation!")
                
                # Message input area
                st.markdown("---")
                
                # Create a form for message input
                with st.form("message_form", clear_on_submit=True):
                    col_input1, col_input2 = st.columns([4, 1])
                    
                    with col_input1:
                        message = st.text_input(
                            "Type your message...",
                            key="new_message",
                            label_visibility="collapsed",
                            placeholder="Type your message here..."
                        )
                    
                    with col_input2:
                        send_btn = st.form_submit_button("Send", type="primary", use_container_width=True)
                    
                    if send_btn and message:
                        if send_message(user_id, st.session_state.chat_with, message):
                            st.session_state.refresh_chat = True
                            st.rerun()
                        else:
                            st.error("Failed to send message")
                
                # Additional chat features
                col_features1, col_features2, col_features3 = st.columns(3)
                
                with col_features1:
                    if st.button("📎 Attach File", use_container_width=True):
                        st.info("File attachment feature coming soon!")
                
                with col_features2:
                    if st.button("📷 Camera", use_container_width=True):
                        st.info("Camera feature coming soon!")
                
                with col_features3:
                    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
                        st.warning("Are you sure you want to clear this chat?")
                        if st.button("Confirm Clear", type="primary"):
                            st.info("Clear chat feature coming soon!")
            
            else:
                st.error("User not found")
                if st.button("Back to conversations"):
                    st.session_state.chat_with = None
                    st.rerun()
        
        else:
            # No chat selected - show welcome/instructions
            st.markdown("""
            ## 💬 Welcome to Chat
            
            Select a conversation from the left panel or start a new chat with a friend.
            
            ### Features:
            
            **📱 Real-time Messaging**  
            Chat with your friends in real-time
            
            **👥 Group Chats**  
            Create group chats for projects or social groups
            
            **📎 File Sharing**  
            Share files and documents (coming soon)
            
            **🔔 Notifications**  
            Get notified of new messages
            
            ### How to start:
            1. Select a friend from the "Friends" list
            2. Or choose an existing conversation
            3. Type your message and hit send!
            
            ### Tips:
            - You can have multiple conversations open
            - Unread messages are marked with a badge
            - Chat history is saved automatically
            """)
            
            # Quick start buttons
            col_q1, col_q2, col_q3 = st.columns(3)
            
            with col_q1:
                if st.button("👥 View All Friends", use_container_width=True):
                    st.session_state.current_page = "Student/Friends"
                    st.rerun()
            
            with col_q2:
                if st.button("📁 Start Group Chat", use_container_width=True):
                    st.session_state.current_page = "Student/Groups"
                    st.rerun()
            
            with col_q3:
                if st.button("⚙️ Chat Settings", use_container_width=True):
                    st.session_state.current_page = "Student/Settings"
                    st.rerun()
    
    # Auto-refresh chat
    if st.session_state.refresh_chat:
        time.sleep(0.5)
        st.session_state.refresh_chat = False
        st.rerun()
    
    # Refresh button
    if st.button("🔄 Refresh", type="secondary"):
        st.rerun()
