import streamlit as st
import pandas as pd
from utils.database import (
    get_all_users, get_user_by_id, update_user_profile
)

def admin_student_management_page():
    """Student Management Page for Admin"""
    st.title("👨‍🎓 Student Management")
    
    # Get all students
    all_users = get_all_users()
    students = [u for u in all_users if u['role'] == 'student']
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["All Students", "Add Student", "Bulk Operations"])
    
    with tab1:
        # All Students
        st.subheader("📋 All Students")
        
        # Search and filters
        col_search1, col_search2, col_search3 = st.columns(3)
        
        with col_search1:
            search_term = st.text_input("🔍 Search students")
        
        with col_search2:
            department_filter = st.selectbox(
                "Filter by department",
                ["All"] + list(set([s.get('department', '') for s in students if s.get('department')]))
            )
        
        with col_search3:
            year_filter = st.selectbox(
                "Filter by year",
                ["All", "1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"]
            )
        
        # Apply filters
        filtered_students = students
        
        if search_term:
            filtered_students = [
                s for s in filtered_students 
                if search_term.lower() in s['first_name'].lower()
                or search_term.lower() in s['last_name'].lower()
                or search_term.lower() in s['email'].lower()
                or search_term.lower() in s.get('student_id', '').lower()
            ]
        
        if department_filter != "All":
            filtered_students = [s for s in filtered_students if s.get('department') == department_filter]
        
        if year_filter != "All":
            filtered_students = [s for s in filtered_students if s.get('year') == year_filter]
        
        # Display students
        if filtered_students:
            st.markdown(f"**Total Students:** {len(filtered_students)}")
            
            # Create a DataFrame for better display
            df_data = []
            for student in filtered_students:
                df_data.append({
                    'ID': student['id'],
                    'Name': f"{student['first_name']} {student['last_name']}",
                    'Email': student['email'],
                    'Student ID': student.get('student_id', ''),
                    'Department': student.get('department', ''),
                    'Year': student.get('year', ''),
                    'Joined': student['created_at'][:10]
                })
            
            df = pd.DataFrame(df_data)
            
            # Display as table with actions
            st.dataframe(
                df,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Student ID": st.column_config.TextColumn("Student ID", width="small"),
                    "Department": st.column_config.TextColumn("Department", width="medium"),
                    "Year": st.column_config.TextColumn("Year", width="small"),
                    "Joined": st.column_config.TextColumn("Joined", width="small"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Student actions
            st.subheader("🎯 Student Actions")
            
            selected_id = st.selectbox(
                "Select Student ID to Manage",
                options=[s['id'] for s in filtered_students],
                format_func=lambda x: f"ID {x} - {next((s['first_name'] + ' ' + s['last_name'] for s in filtered_students if s['id'] == x), '')}"
            )
            
            if selected_id:
                selected_student = next((s for s in filtered_students if s['id'] == selected_id), None)
                
                if selected_student:
                    # Display student details
                    with st.expander(f"Details for {selected_student['first_name']} {selected_student['last_name']}", expanded=True):
                        col_detail1, col_detail2 = st.columns(2)
                        
                        with col_detail1:
                            st.markdown(f"**Student ID:** {selected_student.get('student_id', '')}")
                            st.markdown(f"**Email:** {selected_student['email']}")
                            st.markdown(f"**Phone:** {selected_student.get('phone', 'Not provided')}")
                            st.markdown(f"**Department:** {selected_student.get('department', '')}")
                        
                        with col_detail2:
                            st.markdown(f"**Year:** {selected_student.get('year', '')}")
                            st.markdown(f"**Joined:** {selected_student['created_at'][:10]}")
                            st.markdown(f"**Last Login:** {selected_student.get('last_login', 'Never')[:19]}")
                            if selected_student.get('skills'):
                                st.markdown(f"**Skills:** {selected_student['skills']}")
                        
                        # Management actions
                        st.markdown("### ⚙️ Management Actions")
                        
                        col_action1, col_action2, col_action3, col_action4 = st.columns(4)
                        
                        with col_action1:
                            if st.button("Edit Profile", key=f"edit_{selected_id}"):
                                st.session_state.edit_student_id = selected_id
                                st.rerun()
                        
                        with col_action2:
                            if st.button("View Activity", key=f"activity_{selected_id}"):
                                st.info(f"Activity log for {selected_student['first_name']} coming soon!")
                        
                        with col_action3:
                            if st.button("Send Message", key=f"message_{selected_id}"):
                                st.info(f"Message feature for {selected_student['first_name']} coming soon!")
                        
                        with col_action4:
                            if st.button("Deactivate", key=f"deactivate_{selected_id}", type="secondary"):
                                st.warning(f"Deactivate {selected_student['first_name']}?")
                                if st.button("Confirm Deactivation", key=f"confirm_deact_{selected_id}"):
                                    if update_user_profile(selected_id, is_verified=0):
                                        st.success(f"{selected_student['first_name']} deactivated")
                                        st.rerun()
                                    else:
                                        st.error("Failed to deactivate student")
        else:
            st.info("No students found with the current filters.")
    
    with tab2:
        # Add Student
        st.subheader("👤 Add New Student")
        
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name *")
                email = st.text_input("Email *")
                password = st.text_input("Password *", type="password")
                phone = st.text_input("Phone Number")
                department = st.selectbox("Department *", 
                    ["Computer Science", "Electronics & Communication", "Mechanical", 
                     "Civil", "Electrical", "Information Technology", "Chemical", 
                     "Biotechnology", "Aerospace", "Other"])
            
            with col2:
                last_name = st.text_input("Last Name *")
                student_id = st.text_input("Student ID *")
                confirm_password = st.text_input("Confirm Password *", type="password")
                year = st.selectbox("Academic Year *", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"])
                skills = st.text_area("Skills (comma separated)")
            
            about = st.text_area("About")
            
            submit = st.form_submit_button("Add Student", type="primary")
            
            if submit:
                if not all([first_name, last_name, email, password, confirm_password, student_id, department, year]):
                    st.error("Please fill all required fields (*)")
                elif password != confirm_password:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    try:
                        from utils.database import add_user
                        user_id = add_user(
                            email=email,
                            password=password,
                            role="student",
                            first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            student_id=student_id,
                            department=department,
                            year=year,
                            skills=skills,
                            about=about,
                            is_verified=1  # Auto-verify for admin-added users
                        )
                        if user_id:
                            st.success(f"Student {first_name} {last_name} added successfully!")
                            st.balloons()
                        else:
                            st.error("Failed to add student")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab3:
        # Bulk Operations
        st.subheader("📦 Bulk Operations")
        
        # Import from CSV
        st.markdown("### 📁 Import Students from CSV")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                # Map columns
                st.markdown("### 🗺️ Column Mapping")
                
                col_map1, col_map2 = st.columns(2)
                
                with col_map1:
                    first_name_col = st.selectbox("First Name Column", df.columns)
                    email_col = st.selectbox("Email Column", df.columns)
                    student_id_col = st.selectbox("Student ID Column", df.columns)
                
                with col_map2:
                    last_name_col = st.selectbox("Last Name Column", df.columns)
                    department_col = st.selectbox("Department Column", df.columns)
                    year_col = st.selectbox("Year Column", df.columns)
                
                # Default values
                default_password = st.text_input("Default Password for all students", type="password", value="Password123")
                
                if st.button("Import Students", type="primary"):
                    success_count = 0
                    error_count = 0
                    errors = []
                    
                    for idx, row in df.iterrows():
                        try:
                            from utils.database import add_user
                            user_id = add_user(
                                email=row[email_col],
                                password=default_password,
                                role="student",
                                first_name=row[first_name_col],
                                last_name=row[last_name_col],
                                student_id=row[student_id_col],
                                department=row[department_col],
                                year=row[year_col],
                                is_verified=1
                            )
                            if user_id:
                                success_count += 1
                            else:
                                error_count += 1
                                errors.append(f"Row {idx+1}: Failed to add student")
                        except Exception as e:
                            error_count += 1
                            errors.append(f"Row {idx+1}: {str(e)}")
                    
                    st.success(f"Import complete! Success: {success_count}, Errors: {error_count}")
                    
                    if errors:
                        with st.expander("View Errors"):
                            for error in errors:
                                st.error(error)
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
        
        # Export students
        st.markdown("### 📤 Export Students")
        
        if st.button("Export All Students to CSV", type="secondary"):
            # Create export data
            export_data = []
            for student in students:
                export_data.append({
                    'First Name': student['first_name'],
                    'Last Name': student['last_name'],
                    'Email': student['email'],
                    'Student ID': student.get('student_id', ''),
                    'Department': student.get('department', ''),
                    'Year': student.get('year', ''),
                    'Phone': student.get('phone', ''),
                    'Joined Date': student['created_at'][:10],
                    'Last Login': student.get('last_login', '')[:19] if student.get('last_login') else '',
                    'Skills': student.get('skills', ''),
                    'About': student.get('about', '')
                })
            
            df_export = pd.DataFrame(export_data)
            
            # Convert to CSV
            csv = df_export.to_csv(index=False)
            
            # Download button
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="mes_students_export.csv",
                mime="text/csv"
            )
        
        # Bulk actions
        st.markdown("### ⚡ Bulk Actions")
        
        col_bulk1, col_bulk2, col_bulk3 = st.columns(3)
        
        with col_bulk1:
            if st.button("Send Bulk Email", use_container_width=True):
                st.info("Bulk email feature coming soon!")
        
        with col_bulk2:
            if st.button("Generate Reports", use_container_width=True):
                st.info("Report generation coming soon!")
        
        with col_bulk3:
            if st.button("Update All Profiles", use_container_width=True):
                st.info("Bulk update feature coming soon!")
    
    # Edit Student Modal (if triggered)
    if 'edit_student_id' in st.session_state:
        student = get_user_by_id(st.session_state.edit_student_id)
        
        if student:
            with st.form("edit_student_modal"):
                st.subheader(f"✏️ Edit Student: {student['first_name']} {student['last_name']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_first_name = st.text_input("First Name", value=student['first_name'])
                    edit_email = st.text_input("Email", value=student['email'])
                    edit_phone = st.text_input("Phone", value=student.get('phone', ''))
                    edit_department = st.selectbox(
                        "Department",
                        ["Computer Science", "Electronics & Communication", "Mechanical", 
                         "Civil", "Electrical", "Information Technology", "Chemical", 
                         "Biotechnology", "Aerospace", "Other"],
                        index=["Computer Science", "Electronics & Communication", "Mechanical", 
                              "Civil", "Electrical", "Information Technology", "Chemical", 
                              "Biotechnology", "Aerospace", "Other"].index(student.get('department', 'Computer Science')) 
                              if student.get('department') in ["Computer Science", "Electronics & Communication", "Mechanical", 
                                                             "Civil", "Electrical", "Information Technology", "Chemical", 
                                                             "Biotechnology", "Aerospace", "Other"] else 0
                    )
                
                with col2:
                    edit_last_name = st.text_input("Last Name", value=student['last_name'])
                    edit_student_id = st.text_input("Student ID", value=student.get('student_id', ''))
                    edit_year = st.selectbox(
                        "Academic Year",
                        ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"],
                        index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"].index(student.get('year', '1st Year')) 
                        if student.get('year') in ["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"] else 0
                    )
                    edit_skills = st.text_area("Skills", value=student.get('skills', ''))
                
                edit_about = st.text_area("About", value=student.get('about', ''), height=100)
                
                # Verification status
                is_verified = st.checkbox("Account Verified", value=bool(student.get('is_verified', 1)))
                
                col_submit1, col_submit2 = st.columns([1, 1])
                with col_submit1:
                    save = st.form_submit_button("Save Changes", type="primary")
                with col_submit2:
                    cancel = st.form_submit_button("Cancel")
                
                if save:
                    updates = {
                        'first_name': edit_first_name,
                        'last_name': edit_last_name,
                        'email': edit_email,
                        'phone': edit_phone,
                        'student_id': edit_student_id,
                        'department': edit_department,
                        'year': edit_year,
                        'skills': edit_skills,
                        'about': edit_about,
                        'is_verified': 1 if is_verified else 0
                    }
                    
                    if update_user_profile(student['id'], **updates):
                        st.success("Student profile updated successfully!")
                        del st.session_state.edit_student_id
                        st.rerun()
                    else:
                        st.error("Failed to update student profile")
                
                if cancel:
                    del st.session_state.edit_student_id
                    st.rerun()
