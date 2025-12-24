import streamlit as st
from datetime import datetime, timedelta
from utils.database import (
    get_events, add_event, register_for_event,
    get_user_events, get_user_by_id
)

def student_events_page(user_id):
    """Student Events Page"""
    st.title("📅 Events")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Upcoming Events", "My Events", "Create Event", "Past Events"])
    
    with tab1:
        # Upcoming Events
        st.subheader("🎯 Upcoming Events")
        
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            category_filter = st.selectbox(
                "Filter by category",
                ["All", "Academic", "Cultural", "Sports", "Technical", "Social", "Workshop", "Other"]
            )
        
        with col_filter2:
            date_filter = st.selectbox(
                "Filter by date",
                ["All", "Today", "This Week", "This Month", "Next Month"]
            )
        
        with col_filter3:
            show_registered = st.checkbox("Show only registered events", value=False)
        
        # Get events
        events = get_events(upcoming=True, user_id=user_id)
        
        # Apply filters
        filtered_events = events
        
        if category_filter != "All":
            filtered_events = [e for e in filtered_events if e.get('category') == category_filter.lower()]
        
        if date_filter != "All":
            today = datetime.now().date()
            if date_filter == "Today":
                filtered_events = [e for e in filtered_events if e['event_date'] == today.strftime('%Y-%m-%d')]
            elif date_filter == "This Week":
                week_end = today + timedelta(days=7)
                filtered_events = [e for e in filtered_events if e['event_date'] <= week_end.strftime('%Y-%m-%d')]
            elif date_filter == "This Month":
                month_end = today.replace(day=28) + timedelta(days=4)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                filtered_events = [e for e in filtered_events if e['event_date'] <= month_end.strftime('%Y-%m-%d')]
            elif date_filter == "Next Month":
                next_month = today.replace(day=28) + timedelta(days=4)
                next_month = next_month.replace(day=1)
                next_month_end = next_month.replace(day=28) + timedelta(days=4)
                next_month_end = next_month_end.replace(day=1) - timedelta(days=1)
                filtered_events = [
                    e for e in filtered_events 
                    if e['event_date'] >= next_month.strftime('%Y-%m-%d') 
                    and e['event_date'] <= next_month_end.strftime('%Y-%m-%d')
                ]
        
        if show_registered:
            filtered_events = [e for e in filtered_events if e.get('is_registered')]
        
        # Display events
        if filtered_events:
            for event in filtered_events:
                display_event_card(event, user_id)
        else:
            st.info("No upcoming events found with the current filters.")
    
    with tab2:
        # My Events
        st.subheader("📋 My Events")
        
        # Get user's events
        my_events = get_user_events(user_id, upcoming=True)
        
        if my_events:
            # Tabs for different statuses
            tab_reg, tab_att, tab_canc = st.tabs(["Registered", "Attended", "Cancelled"])
            
            with tab_reg:
                registered = [e for e in my_events if e['status'] == 'registered']
                if registered:
                    for event in registered:
                        display_event_card(event, user_id, show_status=True)
                else:
                    st.info("No registered events.")
            
            with tab_att:
                attended = [e for e in my_events if e['status'] == 'attended']
                if attended:
                    for event in attended:
                        display_event_card(event, user_id, show_status=True)
                else:
                    st.info("No attended events.")
            
            with tab_canc:
                cancelled = [e for e in my_events if e['status'] == 'cancelled']
                if cancelled:
                    for event in cancelled:
                        display_event_card(event, user_id, show_status=True)
                else:
                    st.info("No cancelled events.")
        else:
            st.info("You haven't registered for any events yet.")
    
    with tab3:
        # Create Event
        st.subheader("🎪 Create New Event")
        
        with st.form("create_event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Event Title *", placeholder="e.g., Annual Tech Fest 2024")
                category = st.selectbox(
                    "Category *",
                    ["academic", "cultural", "sports", "technical", "social", "workshop", "other"]
                )
                event_date = st.date_input("Event Date *", min_value=datetime.now().date())
                event_time = st.time_input("Event Time")
            
            with col2:
                description = st.text_area(
                    "Description *",
                    placeholder="Describe your event, agenda, speakers, activities...",
                    height=150
                )
                location = st.text_input("Location", placeholder="e.g., Main Auditorium, Block A")
                venue = st.text_input("Venue Details", placeholder="Floor, Room number, etc.")
                max_participants = st.number_input("Max Participants", min_value=1, value=100)
            
            # Additional options
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                is_public = st.checkbox("Public Event (Visible to everyone)", value=True)
                registration_link = st.text_input("Registration Link", placeholder="https://forms.google.com/...")
            
            with col_opt2:
                cover_pic = st.file_uploader("Event Cover Picture", type=['jpg', 'jpeg', 'png'])
            
            # Submit button
            submit = st.form_submit_button("Create Event", type="primary")
            
            if submit:
                if not all([title, description, event_date]):
                    st.error("Please fill all required fields (*)")
                else:
                    event_data = {
                        'event_time': event_time.strftime('%H:%M:%S'),
                        'location': location,
                        'venue': venue,
                        'max_participants': max_participants if max_participants > 0 else None,
                        'is_public': 1 if is_public else 0,
                        'category': category,
                        'registration_link': registration_link or None
                    }
                    
                    if cover_pic:
                        # Handle cover picture upload
                        import base64
                        image_bytes = cover_pic.read()
                        b64_string = base64.b64encode(image_bytes).decode()
                        event_data['cover_pic'] = f"data:image/jpeg;base64,{b64_string}"
                    
                    event_id = add_event(
                        title=title,
                        description=description,
                        organizer_id=user_id,
                        event_date=event_date.strftime('%Y-%m-%d'),
                        **event_data
                    )
                    
                    if event_id:
                        st.success(f"🎉 Event '{title}' created successfully!")
                        st.balloons()
                        
                        # Show event management options
                        with st.expander("Event Management", expanded=True):
                            st.markdown(f"""
                            ### 🎪 Your event is live!
                            
                            **Event ID:** `{event_id}`
                            **Share Link:** `mes-connect.com/events/{event_id}`
                            
                            **What you can do now:**
                            
                            1. **📢 Promote** - Share the event with friends and groups
                            2. **👥 Manage Registrations** - View and manage participants
                            3. **📝 Update Details** - Make changes to event information
                            4. **📊 Track Attendance** - Monitor event participation
                            5. **📸 Add Photos** - Upload event photos after it's over
                            
                            **Next Steps:**
                            - Check registrations regularly
                            - Send reminders to participants
                            - Prepare event materials
                            - Coordinate with volunteers
                            """)
                            
                            col_manage1, col_manage2 = st.columns(2)
                            with col_manage1:
                                if st.button("View Event", type="primary"):
                                    # Refresh to show event
                                    st.rerun()
                            with col_manage2:
                                if st.button("Share Event"):
                                    st.info("Share feature coming soon!")
                    else:
                        st.error("Failed to create event")
    
    with tab4:
        # Past Events
        st.subheader("📜 Past Events")
        
        # Get past events
        past_events = get_events(upcoming=False, user_id=user_id)
        
        if past_events:
            # Search and filter
            col_search1, col_search2 = st.columns(2)
            
            with col_search1:
                search_term = st.text_input("Search past events")
            
            with col_search2:
                past_category_filter = st.selectbox(
                    "Filter category",
                    ["All", "Academic", "Cultural", "Sports", "Technical", "Social", "Workshop", "Other"]
                )
            
            # Apply filters
            filtered_past = past_events
            
            if search_term:
                filtered_past = [
                    e for e in filtered_past 
                    if search_term.lower() in e['title'].lower()
                    or search_term.lower() in e.get('description', '').lower()
                ]
            
            if past_category_filter != "All":
                filtered_past = [e for e in filtered_past if e.get('category') == past_category_filter.lower()]
            
            # Display past events
            if filtered_past:
                for event in filtered_past[:10]:  # Show first 10
                    display_event_card(event, user_id, is_past=True)
                
                if len(filtered_past) > 10:
                    if st.button("Load More Past Events", type="secondary"):
                        st.info("Pagination feature coming soon!")
            else:
                st.info("No past events found with the current filters.")
        else:
            st.info("No past events available.")

def display_event_card(event, user_id, show_status=False, is_past=False):
    """Display an event card"""
    with st.container():
        st.markdown(f"<div class='event-card'>", unsafe_allow_html=True)
        
        # Event header
        col_header1, col_header2 = st.columns([4, 1])
        
        with col_header1:
            st.markdown(f"### {event['title']}")
            
            # Category badge
            category_colors = {
                'academic': '📚',
                'cultural': '🎭',
                'sports': '⚽',
                'technical': '💻',
                'social': '🎉',
                'workshop': '🔧',
                'other': '📅'
            }
            category_icon = category_colors.get(event.get('category', 'other'), '📅')
            st.caption(f"{category_icon} {event.get('category', 'event').title()}")
        
        with col_header2:
            # Date and time
            event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
            date_str = event_date.strftime('%b %d, %Y')
            st.markdown(f"**{date_str}**")
            if event.get('event_time'):
                st.caption(f"🕒 {event['event_time'][:5]}")
        
        # Event details
        if event.get('description'):
            st.markdown(f"> {event['description'][:200]}...")
            if len(event['description']) > 200:
                with st.expander("Read more"):
                    st.markdown(event['description'])
        
        # Location and participants
        col_details1, col_details2 = st.columns(2)
        
        with col_details1:
            if event.get('location'):
                st.markdown(f"📍 **Location:** {event['location']}")
            if event.get('venue'):
                st.caption(f"🏢 {event['venue']}")
        
        with col_details2:
            st.markdown(f"👥 **Participants:** {event['participant_count']}")
            if event.get('max_participants'):
                st.caption(f"Max: {event['max_participants']}")
        
        # Organizer info
        if event.get('organizer_first_name'):
            st.caption(f"📋 Organized by: {event['organizer_first_name']} {event['organizer_last_name']}")
        
        # Action buttons
        col_actions1, col_actions2, col_actions3 = st.columns(3)
        
        with col_actions1:
            if is_past:
                st.info("Event Ended")
            elif event.get('is_registered'):
                st.success("✅ Registered")
            else:
                if st.button("Register", key=f"reg_{event['id']}", type="primary"):
                    success, msg = register_for_event(event['id'], user_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        with col_actions2:
            if st.button("View Details", key=f"view_{event['id']}"):
                with st.expander("Event Details", expanded=True):
                    # Full event details
                    st.markdown(f"**Title:** {event['title']}")
                    st.markdown(f"**Date:** {event['event_date']}")
                    if event.get('event_time'):
                        st.markdown(f"**Time:** {event['event_time'][:5]}")
                    if event.get('location'):
                        st.markdown(f"**Location:** {event['location']}")
                    if event.get('venue'):
                        st.markdown(f"**Venue Details:** {event['venue']}")
                    if event.get('max_participants'):
                        st.markdown(f"**Max Participants:** {event['max_participants']}")
                    if event.get('registration_link'):
                        st.markdown(f"**Registration:** [Link]({event['registration_link']})")
                    
                    st.markdown("**Description:**")
                    st.markdown(event['description'])
                    
                    # Show status if applicable
                    if show_status:
                        st.markdown(f"**Your Status:** {event['status'].title()}")
                    
                    # Additional actions
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        if not is_past and not event.get('is_registered'):
                            if st.button("Register Here", key=f"reg_exp_{event['id']}"):
                                success, msg = register_for_event(event['id'], user_id)
                                if success:
                                    st.success(msg)
                                    st.rerun()
                    with col_exp2:
                        if st.button("Share Event", key=f"share_{event['id']}"):
                            st.info("Share feature coming soon!")
        
        with col_actions3:
            if st.button("📅 Add to Calendar", key=f"cal_{event['id']}"):
                st.info("Calendar integration coming soon!")
        
        # Status display
        if show_status:
            status_colors = {
                'registered': '🟡',
                'attended': '🟢',
                'cancelled': '🔴'
            }
            status_icon = status_colors.get(event['status'], '⚪')
            st.caption(f"{status_icon} Your status: {event['status'].title()}")
        
        st.markdown("</div>", unsafe_allow_html=True)
