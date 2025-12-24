import streamlit as st
from datetime import datetime, timedelta
from utils.database import (
    get_events, add_event, register_for_event,
    get_user_events, get_user_by_id
)

def alumni_events_page(user_id):
    """Alumni Events Page"""
    st.title("📅 Alumni Events")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Upcoming Events", "My Events", "Create Event", "Past Events"
    ])
    
    with tab1:
        # Upcoming Events
        st.subheader("🎯 Upcoming Alumni Events")
        
        # Filters for alumni
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            category_filter = st.selectbox(
                "Filter by category",
                ["All", "Networking", "Career", "Alumni Reunion", "Workshop", 
                 "Mentorship", "Social", "Other"]
            )
        
        with col_filter2:
            audience_filter = st.selectbox(
                "Filter by audience",
                ["All", "Alumni Only", "Students & Alumni", "Public"]
            )
        
        with col_filter3:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest", "Date", "Popularity"]
            )
        
        # Get events
        events = get_events(upcoming=True, user_id=user_id)
        
        # Filter for alumni-relevant events
        alumni_events = []
        for event in events:
            # Check if event is relevant for alumni
            if event.get('category') in ['networking', 'career', 'alumni', 'reunion', 'workshop']:
                alumni_events.append(event)
            elif 'alumni' in event.get('description', '').lower():
                alumni_events.append(event)
            elif event.get('organizer_role') == 'alumni':
                alumni_events.append(event)
            else:
                alumni_events.append(event)  # Show all events for now
        
        # Apply filters
        filtered_events = alumni_events
        
        if category_filter != "All":
            filtered_events = [e for e in filtered_events if e.get('category') == category_filter.lower()]
        
        # Display events
        if filtered_events:
            for event in filtered_events:
                display_alumni_event_card(event, user_id)
        else:
            st.info("No upcoming alumni events found.")
    
    with tab2:
        # My Events
        st.subheader("📋 My Events")
        
        # Get user's events
        my_events = get_user_events(user_id, upcoming=True)
        
        if my_events:
            # Organize by role
            events_organized = [e for e in get_events(upcoming=True) if e.get('organizer_id') == user_id]
            events_registered = [e for e in my_events if e['status'] == 'registered' and e.get('organizer_id') != user_id]
            
            # Events organized
            if events_organized:
                st.markdown("### 🎪 Events I'm Organizing")
                for event in events_organized:
                    display_alumni_event_card(event, user_id, is_organizer=True)
            
            # Events registered for
            if events_registered:
                st.markdown("### 📅 Events I'm Attending")
                for event in events_registered:
                    display_alumni_event_card(event, user_id)
        else:
            st.info("You haven't registered for any events yet.")
    
    with tab3:
        # Create Event
        st.subheader("🎪 Create Alumni Event")
        
        with st.form("create_alumni_event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Event Title *", placeholder="e.g., Alumni Networking Mixer 2024")
                event_type = st.selectbox(
                    "Event Type *",
                    ["Networking", "Career Fair", "Alumni Reunion", "Workshop/Seminar", 
                     "Mentorship Session", "Social Gathering", "Fundraiser", "Other"]
                )
                target_audience = st.multiselect(
                    "Target Audience *",
                    ["Alumni", "Students", "Faculty", "Public"]
                )
                event_date = st.date_input("Event Date *", min_value=datetime.now().date())
                event_time = st.time_input("Event Time")
            
            with col2:
                description = st.text_area(
                    "Description *",
                    placeholder="Describe your event, agenda, speakers, activities...\n\nFor alumni events, include:\n- Purpose of the event\n- Who should attend\n- What to expect\n- Any special requirements",
                    height=150
                )
                location = st.text_input("Location", placeholder="e.g., Hotel Grand, Downtown")
                venue_details = st.text_input("Venue Details", placeholder="Conference Room, Floor, etc.")
                max_participants = st.number_input("Max Participants", min_value=1, value=50)
            
            # Alumni-specific options
            col_alum1, col_alum2 = st.columns(2)
            
            with col_alum1:
                is_virtual = st.checkbox("Virtual/Online Event", value=False)
                if is_virtual:
                    meeting_link = st.text_input("Meeting Link", placeholder="Zoom, Google Meet, etc.")
                else:
                    meeting_link = None
                
                has_sponsors = st.checkbox("Has Sponsors", value=False)
                if has_sponsors:
                    sponsors = st.text_area("Sponsor Information")
            
            with col_alum2:
                require_rsvp = st.checkbox("Require RSVP", value=True)
                is_exclusive = st.checkbox("Exclusive to MES Community", value=True)
                cover_charge = st.number_input("Cover Charge ($)", min_value=0, value=0)
            
            # Event image
            cover_pic = st.file_uploader("Event Banner/Poster", type=['jpg', 'jpeg', 'png'])
            
            # Submit button
            submit = st.form_submit_button("Create Alumni Event", type="primary")
            
            if submit:
                if not all([title, description, event_date, target_audience]):
                    st.error("Please fill all required fields (*)")
                else:
                    # Prepare event data
                    event_data = {
                        'event_time': event_time.strftime('%H:%M:%S'),
                        'location': location,
                        'venue': venue_details,
                        'max_participants': max_participants if max_participants > 0 else None,
                        'is_public': 1 if 'Public' in target_audience else 0,
                        'category': event_type.lower(),
                        'registration_link': meeting_link if is_virtual else None
                    }
                    
                    # Add alumni-specific information to description
                    full_description = f"{description}\n\n"
                    full_description += f"**Event Type:** {event_type}\n"
                    full_description += f"**Target Audience:** {', '.join(target_audience)}\n"
                    if is_virtual:
                        full_description += f"**Virtual Event:** Yes\n"
                    if has_sponsors:
                        full_description += f"**Sponsors:** {sponsors}\n"
                    if cover_charge > 0:
                        full_description += f"**Cover Charge:** ${cover_charge}\n"
                    if is_exclusive:
                        full_description += f"**Exclusive to MES Community:** Yes\n"
                    
                    if cover_pic:
                        import base64
                        image_bytes = cover_pic.read()
                        b64_string = base64.b64encode(image_bytes).decode()
                        event_data['cover_pic'] = f"data:image/jpeg;base64,{b64_string}"
                    
                    event_id = add_event(
                        title=title,
                        description=full_description,
                        organizer_id=user_id,
                        event_date=event_date.strftime('%Y-%m-%d'),
                        **event_data
                    )
                    
                    if event_id:
                        st.success(f"🎉 Alumni event '{title}' created successfully!")
                        st.balloons()
                        
                        with st.expander("Event Management Tips", expanded=True):
                            st.markdown(f"""
                            ### 🎪 Your alumni event is live!
                            
                            **Event ID:** `{event_id}`
                            **Share Link:** `mes-connect.com/events/{event_id}`
                            
                            **For Alumni Events:**
                            
                            1. **📢 Promote Widely** - Share across alumni networks
                            2. **👥 Target Right Audience** - Reach out to relevant alumni
                            3. **💼 Add Value** - Ensure event provides networking/career value
                            4. **📝 Collect Feedback** - Gather insights for future events
                            5. **🤝 Foster Connections** - Facilitate networking during event
                            
                            **Next Steps:**
                            - Share on LinkedIn and other professional networks
                            - Send personalized invites to key alumni
                            - Prepare talking points and discussion topics
                            - Arrange for photography/videography
                            - Plan follow-up activities
                            """)
                            
                            col_manage1, col_manage2 = st.columns(2)
                            with col_manage1:
                                if st.button("View Event", type="primary"):
                                    st.rerun()
                            with col_manage2:
                                if st.button("Invite Alumni"):
                                    st.info("Bulk invitation feature coming soon!")
                    else:
                        st.error("Failed to create event")
    
    with tab4:
        # Past Events
        st.subheader("📜 Past Alumni Events")
        
        # Get past events
        past_events = get_events(upcoming=False, user_id=user_id)
        
        # Filter for alumni events
        past_alumni_events = []
        for event in past_events:
            if event.get('category') in ['networking', 'career', 'alumni', 'reunion']:
                past_alumni_events.append(event)
            elif 'alumni' in event.get('description', '').lower():
                past_alumni_events.append(event)
        
        if past_alumni_events:
            # Search past events
            search_past = st.text_input("🔍 Search past alumni events")
            
            filtered_past = past_alumni_events
            if search_past:
                filtered_past = [
                    e for e in past_alumni_events 
                    if search_past.lower() in e['title'].lower()
                    or search_past.lower() in e.get('description', '').lower()
                ]
            
            # Display past events
            if filtered_past:
                cols = st.columns(2)
                for idx, event in enumerate(filtered_past[:6]):  # Show max 6
                    with cols[idx % 2]:
                        display_alumni_event_card(event, user_id, is_past=True)
                
                if len(filtered_past) > 6:
                    if st.button("Load More Past Events", type="secondary"):
                        st.info("Pagination feature coming soon!")
            else:
                st.info("No past alumni events found with the current search.")
        else:
            st.info("No past alumni events available.")

def display_alumni_event_card(event, user_id, is_organizer=False, is_past=False):
    """Display an alumni event card"""
    with st.container():
        st.markdown(f"<div class='event-card'>", unsafe_allow_html=True)
        
        # Event header
        col_header1, col_header2 = st.columns([4, 1])
        
        with col_header1:
            st.markdown(f"### {event['title']}")
            
            # Event type badge
            type_icons = {
                'networking': '🤝',
                'career': '💼',
                'reunion': '👨‍🎓',
                'workshop': '🎓',
                'mentorship': '👨‍🏫',
                'social': '🎉',
                'fundraiser': '💰',
                'other': '📅'
            }
            event_type = event.get('category', 'other')
            type_icon = type_icons.get(event_type, '📅')
            st.caption(f"{type_icon} {event_type.title()}")
            
            if is_organizer:
                st.caption("🎪 **You are organizing this event**")
        
        with col_header2:
            # Date and time
            event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
            date_str = event_date.strftime('%b %d, %Y')
            st.markdown(f"**{date_str}**")
            if event.get('event_time'):
                st.caption(f"🕒 {event['event_time'][:5]}")
        
        # Event description preview
        if event.get('description'):
            # Extract first paragraph for preview
            desc_lines = event['description'].split('\n')
            preview = desc_lines[0][:200] + "..." if len(desc_lines[0]) > 200 else desc_lines[0]
            st.markdown(f"> {preview}")
            
            # Show more details in expander
            with st.expander("Event Details"):
                st.markdown(event['description'])
                
                # Show additional info for alumni events
                if '**Event Type:**' in event['description']:
                    st.markdown("### 📋 Event Information")
                    for line in event['description'].split('\n'):
                        if line.startswith('**'):
                            st.markdown(line)
        
        # Location and participants
        col_details1, col_details2 = st.columns(2)
        
        with col_details1:
            if event.get('location'):
                st.markdown(f"📍 **Location:** {event['location']}")
            if event.get('venue'):
                st.caption(f"🏢 {event['venue']}")
            
            # Check if virtual
            if 'Virtual Event: Yes' in event.get('description', ''):
                st.caption("🌐 **Virtual Event**")
        
        with col_details2:
            st.markdown(f"👥 **Participants:** {event['participant_count']}")
            if event.get('max_participants'):
                st.caption(f"Max: {event['max_participants']}")
            
            # Check for cover charge
            if 'Cover Charge:' in event.get('description', ''):
                for line in event['description'].split('\n'):
                    if 'Cover Charge:' in line:
                        st.caption(line)
                        break
        
        # Organizer info
        if event.get('organizer_first_name'):
            st.caption(f"📋 Organized by: {event['organizer_first_name']} {event['organizer_last_name']}")
            
            # Show if organizer is alumni
            organizer_info = get_user_by_id(event['organizer_id'])
            if organizer_info and organizer_info['role'] == 'alumni':
                st.caption("👨‍🎓 **Alumni-Organized Event**")
        
        # Action buttons
        col_actions1, col_actions2, col_actions3 = st.columns(3)
        
        with col_actions1:
            if is_past:
                st.info("Event Ended")
                # Add feedback button for past events
                if st.button("Leave Feedback", key=f"feedback_{event['id']}"):
                    st.info("Feedback feature coming soon!")
            elif event.get('is_registered'):
                st.success("✅ Registered")
            else:
                if st.button("Register", key=f"alum_reg_{event['id']}", type="primary"):
                    success, msg = register_for_event(event['id'], user_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        with col_actions2:
            if st.button("View Details", key=f"alum_view_{event['id']}"):
                with st.expander("Full Event Details", expanded=True):
                    # Display all event information
                    st.markdown(f"**Title:** {event['title']}")
                    st.markdown(f"**Date:** {event['event_date']}")
                    if event.get('event_time'):
                        st.markdown(f"**Time:** {event['event_time'][:5]}")
                    if event.get('location'):
                        st.markdown(f"**Location:** {event['location']}")
                    if event.get('venue'):
                        st.markdown(f"**Venue Details:** {event['venue']}")
                    
                    # Show alumni-specific info
                    st.markdown("**Description:**")
                    st.markdown(event['description'])
                    
                    # Registration button in details
                    if not is_past and not event.get('is_registered'):
                        if st.button("Register Here", key=f"reg_exp_{event['id']}"):
                            success, msg = register_for_event(event['id'], user_id)
                            if success:
                                st.success(msg)
                                st.rerun()
        
        with col_actions3:
            # Share button for networking events
            if event_type == 'networking' or event_type == 'career':
                if st.button("🤝 Share with Network", key=f"share_alum_{event['id']}"):
                    st.info("Share with your professional network!")
            else:
                if st.button("📅 Add to Calendar", key=f"alum_cal_{event['id']}"):
                    st.info("Calendar integration coming soon!")
        
        # Organizer tools
        if is_organizer and not is_past:
            st.markdown("---")
            st.subheader("🎪 Organizer Tools")
            
            col_org1, col_org2, col_org3 = st.columns(3)
            
            with col_org1:
                if st.button("Manage Registrations", key=f"manage_reg_{event['id']}"):
                    st.info("Registration management coming soon!")
            
            with col_org2:
                if st.button("Send Updates", key=f"updates_{event['id']}"):
                    st.info("Update system coming soon!")
            
            with col_org3:
                if st.button("Event Analytics", key=f"analytics_{event['id']}"):
                    st.info("Analytics dashboard coming soon!")
        
        st.markdown("</div>", unsafe_allow_html=True)
