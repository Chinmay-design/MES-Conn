import streamlit as st
from datetime import datetime
from utils.database import (
    get_confessions, add_confession, like_confession,
    get_user_by_id
)

def student_confessions_page(user_id):
    """Student Confessions Page"""
    st.title("📝 Confessions")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["View Confessions", "Post Confession", "My Confessions"])
    
    with tab1:
        # View Confessions
        st.subheader("💭 Latest Confessions")
        
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest", "Most Liked", "Oldest"]
            )
        
        with col_filter2:
            tags_filter = st.multiselect(
                "Filter by tags",
                ["Love", "Friendship", "College Life", "Study", "Advice", "Funny", "Serious", "Other"]
            )
        
        with col_filter3:
            show_anonymous = st.checkbox("Show only anonymous", value=False)
        
        # Get confessions
        confessions = get_confessions(status='approved', limit=100)
        
        # Apply filters
        filtered_confessions = confessions
        
        if show_anonymous:
            filtered_confessions = [c for c in filtered_confessions if c['is_anonymous'] == 1]
        
        if tags_filter:
            filtered_confessions = [
                c for c in filtered_confessions 
                if c.get('tags') and any(tag in c['tags'] for tag in tags_filter)
            ]
        
        # Sort
        if sort_by == "Newest":
            filtered_confessions.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == "Most Liked":
            filtered_confessions.sort(key=lambda x: x.get('like_count', 0), reverse=True)
        elif sort_by == "Oldest":
            filtered_confessions.sort(key=lambda x: x['created_at'])
        
        # Display confessions
        if filtered_confessions:
            for confession in filtered_confessions:
                display_confession_card(confession, user_id)
        else:
            st.info("No confessions found with the current filters.")
    
    with tab2:
        # Post Confession
        st.subheader("✍️ Post a Confession")
        
        with st.form("post_confession_form"):
            # Confession content
            content = st.text_area(
                "Your Confession *",
                placeholder="Share your thoughts, feelings, or experiences...",
                height=200,
                help="Be respectful and considerate. Anonymous confessions will not reveal your identity."
            )
            
            # Options
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                is_anonymous = st.checkbox("Post anonymously", value=True)
                tags = st.multiselect(
                    "Add tags",
                    ["Love", "Friendship", "College Life", "Study", "Advice", "Funny", "Serious", "Other"]
                )
            
            with col_opt2:
                st.markdown("### Guidelines")
                st.markdown("""
                - ✅ Be respectful
                - ✅ Keep it positive
                - ✅ No personal attacks
                - ✅ No hate speech
                - ✅ Follow community rules
                
                *Confessions are moderated*
                """)
            
            # Submit button
            submit = st.form_submit_button("Post Confession", type="primary")
            
            if submit:
                if not content.strip():
                    st.error("Please write a confession")
                elif len(content.strip()) < 10:
                    st.error("Confession is too short (minimum 10 characters)")
                elif len(content.strip()) > 1000:
                    st.error("Confession is too long (maximum 1000 characters)")
                else:
                    # Convert tags to string
                    tags_str = ','.join(tags) if tags else None
                    
                    # Add confession
                    confession_id = add_confession(
                        user_id=None if is_anonymous else user_id,
                        content=content.strip(),
                        is_anonymous=is_anonymous,
                        tags=tags_str
                    )
                    
                    if confession_id:
                        st.success("🎉 Confession posted successfully!")
                        st.balloons()
                        
                        st.markdown("""
                        ### What happens next?
                        
                        1. **Moderation** - Your confession will be reviewed by moderators
                        2. **Approval** - If it follows guidelines, it will be approved
                        3. **Publication** - It will appear in the confessions feed
                        4. **Likes & Comments** - Others can react to it
                        
                        *Note: Anonymous confessions cannot be traced back to you*
                        """)
                        
                        if st.button("View My Confession"):
                            st.session_state.current_page = "Student/Confessions"
                            st.rerun()
                    else:
                        st.error("Failed to post confession")
    
    with tab3:
        # My Confessions
        st.subheader("My Confessions")
        
        # Get all confessions and filter by user
        all_confessions = get_confessions(status='all', limit=200)
        my_confessions = [c for c in all_confessions if c.get('user_id') == user_id]
        
        if my_confessions:
            # Status filter
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "Pending", "Approved", "Rejected"]
            )
            
            filtered_my_confessions = my_confessions
            if status_filter != "All":
                filtered_my_confessions = [c for c in my_confessions if c['status'] == status_filter.lower()]
            
            if filtered_my_confessions:
                for confession in filtered_my_confessions:
                    display_confession_card(confession, user_id, show_status=True)
            else:
                st.info(f"No {status_filter.lower()} confessions found.")
        else:
            st.info("You haven't posted any confessions yet.")
            
            st.markdown("""
            ### Why post a confession?
            
            **🤫 Anonymous Sharing**  
            Share your thoughts without revealing your identity
            
            **❤️ Get Support**  
            Receive likes and positive reactions from the community
            
            **🤝 Connect**  
            Find others who relate to your experiences
            
            **🎯 Campus Pulse**  
            Be part of the campus conversation
            
            **Ready to share?** Go to the "Post Confession" tab!
            """)

def display_confession_card(confession, user_id, show_status=False):
    """Display a confession card"""
    with st.container():
        st.markdown(f"<div class='confession-card'>", unsafe_allow_html=True)
        
        # Header with author info
        col_header1, col_header2 = st.columns([4, 1])
        
        with col_header1:
            if confession['is_anonymous']:
                author = "Anonymous"
                avatar = "👤"
            else:
                # Try to get user info
                if confession.get('first_name'):
                    author = f"{confession['first_name']}"
                    if confession.get('last_name'):
                        author += f" {confession['last_name'][0]}."
                else:
                    author = "User"
                avatar = "👤"
            
            st.markdown(f"{avatar} **{author}**")
            
            # Tags
            if confession.get('tags'):
                tags = confession['tags'].split(',')
                tag_text = " ".join([f"`#{tag}`" for tag in tags])
                st.markdown(tag_text)
        
        with col_header2:
            # Like button and count
            like_count = confession.get('like_count', 0)
            user_liked = confession.get('user_liked', 0)
            
            like_icon = "❤️" if user_liked else "🤍"
            if st.button(f"{like_icon} {like_count}", key=f"like_{confession['id']}"):
                if like_confession(confession['id'], user_id):
                    st.rerun()
        
        # Confession content
        st.markdown(f"> *{confession['content']}*")
        
        # Footer
        col_footer1, col_footer2 = st.columns([3, 1])
        
        with col_footer1:
            # Date and time
            created_at = datetime.strptime(confession['created_at'], '%Y-%m-%d %H:%M:%S')
            time_ago = get_time_ago(created_at)
            st.caption(f"🕒 {time_ago}")
            
            # Status (if showing)
            if show_status:
                status_colors = {
                    'pending': '🟡',
                    'approved': '🟢',
                    'rejected': '🔴'
                }
                status_icon = status_colors.get(confession['status'], '⚪')
                st.caption(f"{status_icon} {confession['status'].title()}")
        
        with col_footer2:
            # Options menu
            with st.popover("⋯"):
                if st.button("Share", key=f"share_{confession['id']}"):
                    st.info("Share feature coming soon!")
                
                if st.button("Report", key=f"report_{confession['id']}"):
                    st.warning("Report feature coming soon!")
                
                # Only show delete for own non-anonymous confessions
                if not confession['is_anonymous'] and confession.get('user_id') == user_id:
                    if st.button("Delete", key=f"delete_{confession['id']}"):
                        st.warning("Delete feature coming soon!")
        
        st.markdown("</div>", unsafe_allow_html=True)

def get_time_ago(dt):
    """Convert datetime to relative time string"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
