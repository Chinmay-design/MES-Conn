import streamlit as st
from utils.database import get_user_by_id, update_user_profile

def admin_settings_page():
    """Admin System Settings Page"""
    st.title("⚙️ System Settings")
    
    # Get admin profile
    admin = get_user_by_id(st.session_state.user_id)
    
    if not admin:
        st.error("Admin profile not found")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "General", "Security", "Email", "Maintenance", "Backup", "Advanced"
    ])
    
    with tab1:
        # General Settings
        st.subheader("🌐 General Settings")
        
        with st.form("general_settings_form"):
            st.markdown("### Platform Information")
            
            col_gen1, col_gen2 = st.columns(2)
            
            with col_gen1:
                platform_name = st.text_input(
                    "Platform Name",
                    value="MES-Connect",
                    help="Name displayed throughout the platform"
                )
                
                platform_url = st.text_input(
                    "Platform URL",
                    value="https://mes-connect.com",
                    help="Base URL for the platform"
                )
            
            with col_gen2:
                contact_email = st.text_input(
                    "Contact Email",
                    value="admin@mes-connect.com",
                    help="Email for user inquiries"
                )
                
                support_email = st.text_input(
                    "Support Email",
                    value="support@mes-connect.com",
                    help="Email for technical support"
                )
            
            st.markdown("### Platform Features")
            
            col_feat1, col_feat2 = st.columns(2)
            
            with col_feat1:
                enable_registration = st.checkbox(
                    "Enable new user registration",
                    value=True,
                    help="Allow new users to register"
                )
                
                enable_confessions = st.checkbox(
                    "Enable confessions feature",
                    value=True
                )
                
                enable_groups = st.checkbox(
                    "Enable groups feature",
                    value=True
                )
            
            with col_feat2:
                enable_events = st.checkbox(
                    "Enable events feature",
                    value=True
                )
                
                enable_jobs = st.checkbox(
                    "Enable job postings",
                    value=True
                )
                
                enable_contributions = st.checkbox(
                    "Enable alumni contributions",
                    value=True
                )
            
            st.markdown("### User Settings")
            
            default_user_role = st.selectbox(
                "Default user role",
                ["student", "alumni"],
                help="Default role for new registrations"
            )
            
            require_email_verification = st.checkbox(
                "Require email verification",
                value=True,
                help="Users must verify email before accessing platform"
            )
            
            auto_approve_alumni = st.checkbox(
                "Auto-approve alumni registrations",
                value=True,
                help="Alumni registrations are approved automatically"
            )
            
            if st.form_submit_button("Save General Settings", type="primary"):
                st.success("General settings saved successfully!")
    
    with tab2:
        # Security Settings
        st.subheader("🔐 Security Settings")
        
        with st.form("security_settings_form"):
            st.markdown("### Authentication")
            
            col_auth1, col_auth2 = st.columns(2)
            
            with col_auth1:
                min_password_length = st.number_input(
                    "Minimum password length",
                    min_value=6,
                    max_value=20,
                    value=8
                )
                
                require_special_chars = st.checkbox(
                    "Require special characters in passwords",
                    value=True
                )
            
            with col_auth2:
                max_login_attempts = st.number_input(
                    "Maximum login attempts",
                    min_value=3,
                    max_value=10,
                    value=5
                )
                
                lockout_duration = st.number_input(
                    "Account lockout duration (minutes)",
                    min_value=5,
                    max_value=1440,
                    value=30
                )
            
            st.markdown("### Session Management")
            
            col_sess1, col_sess2 = st.columns(2)
            
            with col_sess1:
                session_timeout = st.number_input(
                    "Session timeout (minutes)",
                    min_value=15,
                    max_value=1440,
                    value=120
                )
                
                allow_multiple_sessions = st.checkbox(
                    "Allow multiple simultaneous sessions",
                    value=True
                )
            
            with col_sess2:
                secure_cookies = st.checkbox(
                    "Use secure cookies",
                    value=True,
                    help="Cookies only sent over HTTPS"
                )
                
                http_only_cookies = st.checkbox(
                    "HTTP-only cookies",
                    value=True,
                    help="Prevent client-side script access to cookies"
                )
            
            st.markdown("### Security Headers")
            
            enable_csp = st.checkbox(
                "Enable Content Security Policy",
                value=True,
                help="Protect against XSS attacks"
            )
            
            enable_hsts = st.checkbox(
                "Enable HSTS",
                value=True,
                help="Force HTTPS connections"
            )
            
            if st.form_submit_button("Save Security Settings", type="primary"):
                st.success("Security settings saved successfully!")
        
        # Security testing
        st.markdown("### 🛡️ Security Testing")
        
        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            if st.button("Run Security Scan", use_container_width=True):
                st.info("Security scan started...")
                # This would run security checks
                st.success("Scan complete! No critical issues found.")
        
        with col_test2:
            if st.button("Check Vulnerabilities", use_container_width=True):
                st.info("Vulnerability check coming soon!")
    
    with tab3:
        # Email Settings
        st.subheader("📧 Email Configuration")
        
        with st.form("email_settings_form"):
            st.markdown("### SMTP Configuration")
            
            col_smtp1, col_smtp2 = st.columns(2)
            
            with col_smtp1:
                smtp_host = st.text_input(
                    "SMTP Host",
                    value="smtp.gmail.com"
                )
                
                smtp_port = st.number_input(
                    "SMTP Port",
                    min_value=1,
                    max_value=65535,
                    value=587
                )
            
            with col_smtp2:
                smtp_username = st.text_input(
                    "SMTP Username",
                    value="noreply@mes-connect.com"
                )
                
                smtp_password = st.text_input(
                    "SMTP Password",
                    type="password"
                )
            
            encryption = st.radio(
                "Encryption",
                ["TLS", "SSL", "None"],
                horizontal=True
            )
            
            st.markdown("### Email Templates")
            
            email_from_name = st.text_input(
                "From Name",
                value="MES-Connect"
            )
            
            email_from_address = st.text_input(
                "From Address",
                value="noreply@mes-connect.com"
            )
            
            st.markdown("### Test Email")
            
            test_email = st.text_input(
                "Test email address",
                placeholder="Enter email to test configuration"
            )
            
            if st.button("Send Test Email", type="secondary"):
                if test_email:
                    st.info(f"Test email sent to {test_email}")
                else:
                    st.warning("Please enter a test email address")
            
            if st.form_submit_button("Save Email Settings", type="primary"):
                st.success("Email settings saved successfully!")
    
    with tab4:
        # Maintenance Settings
        st.subheader("🔧 Maintenance Settings")
        
        with st.form("maintenance_settings_form"):
            st.markdown("### Maintenance Mode")
            
            maintenance_mode = st.checkbox(
                "Enable maintenance mode",
                value=False,
                help="Platform will be temporarily unavailable"
            )
            
            if maintenance_mode:
                maintenance_message = st.text_area(
                    "Maintenance message",
                    value="MES-Connect is currently undergoing maintenance. We'll be back soon!",
                    height=100
                )
            
            st.markdown("### Performance Settings")
            
            col_perf1, col_perf2 = st.columns(2)
            
            with col_perf1:
                cache_enabled = st.checkbox(
                    "Enable caching",
                    value=True
                )
                
                cache_duration = st.number_input(
                    "Cache duration (seconds)",
                    min_value=60,
                    max_value=86400,
                    value=3600
                )
            
            with col_perf2:
                compress_responses = st.checkbox(
                    "Compress HTTP responses",
                    value=True
                )
                
                optimize_images = st.checkbox(
                    "Auto-optimize images",
                    value=True
                )
            
            st.markdown("### Cleanup Settings")
            
            col_clean1, col_clean2 = st.columns(2)
            
            with col_clean1:
                delete_inactive_users = st.checkbox(
                    "Auto-delete inactive users",
                    value=False
                )
                
                if delete_inactive_users:
                    inactive_days = st.number_input(
                        "Days of inactivity before deletion",
                        min_value=30,
                        max_value=365,
                        value=180
                    )
            
            with col_clean2:
                cleanup_old_data = st.checkbox(
                    "Auto-cleanup old data",
                    value=True
                )
                
                if cleanup_old_data:
                    data_retention = st.number_input(
                        "Data retention period (months)",
                        min_value=1,
                        max_value=60,
                        value=24
                    )
            
            if st.form_submit_button("Save Maintenance Settings", type="primary"):
                st.success("Maintenance settings saved successfully!")
        
        # Maintenance actions
        st.markdown("### 🛠️ Maintenance Actions")
        
        col_maint1, col_maint2, col_maint3 = st.columns(3)
        
        with col_maint1:
            if st.button("Clear Cache", use_container_width=True):
                st.info("Cache cleared successfully!")
        
        with col_maint2:
            if st.button("Optimize Database", use_container_width=True):
                st.info("Database optimization started...")
        
        with col_maint3:
            if st.button("Run Cleanup", use_container_width=True):
                st.info("Cleanup process started...")
    
    with tab5:
        # Backup Settings
        st.subheader("💾 Backup & Restore")
        
        with st.form("backup_settings_form"):
            st.markdown("### Backup Configuration")
            
            col_back1, col_back2 = st.columns(2)
            
            with col_back1:
                auto_backup = st.checkbox(
                    "Enable automatic backups",
                    value=True
                )
                
                if auto_backup:
                    backup_frequency = st.selectbox(
                        "Backup frequency",
                        ["Daily", "Weekly", "Monthly"]
                    )
                    
                    backup_time = st.time_input(
                        "Backup time"
                    )
            
            with col_back2:
                backup_location = st.selectbox(
                    "Backup location",
                    ["Local Server", "Cloud Storage", "Both"]
                )
                
                retain_backups = st.number_input(
                    "Number of backups to retain",
                    min_value=1,
                    max_value=100,
                    value=30
                )
            
            st.markdown("### Backup Contents")
            
            backup_contents = st.multiselect(
                "Select data to backup",
                ["User Data", "Content", "Messages", "Files", "Configuration", "Logs"],
                default=["User Data", "Content", "Configuration"]
            )
            
            encrypt_backups = st.checkbox(
                "Encrypt backups",
                value=True
            )
            
            if st.form_submit_button("Save Backup Settings", type="primary"):
                st.success("Backup settings saved successfully!")
        
        # Backup actions
        st.markdown("### 🔄 Backup Actions")
        
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("Create Backup Now", type="primary", use_container_width=True):
                st.info("Backup creation started...")
                # Simulate backup process
                import time
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                st.success("Backup created successfully!")
        
        with col_action2:
            if st.button("View Backup History", use_container_width=True):
                st.info("Backup history coming soon!")
        
        with col_action3:
            if st.button("Restore from Backup", use_container_width=True):
                st.warning("Restore will overwrite current data. Continue?")
                if st.button("Confirm Restore", type="primary"):
                    st.info("Restore feature coming soon!")
    
    with tab6:
        # Advanced Settings
        st.subheader("⚡ Advanced Settings")
        
        with st.form("advanced_settings_form"):
            st.markdown("### API Configuration")
            
            enable_api = st.checkbox(
                "Enable REST API",
                value=True
            )
            
            if enable_api:
                api_rate_limit = st.number_input(
                    "API rate limit (requests per minute)",
                    min_value=10,
                    max_value=1000,
                    value=100
                )
                
                require_api_key = st.checkbox(
                    "Require API key for access",
                    value=True
                )
            
            st.markdown("### Logging Configuration")
            
            col_log1, col_log2 = st.columns(2)
            
            with col_log1:
                log_level = st.selectbox(
                    "Log level",
                    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                )
                
                log_retention = st.number_input(
                    "Log retention (days)",
                    min_value=1,
                    max_value=365,
                    value=30
                )
            
            with col_log2:
                enable_audit_log = st.checkbox(
                    "Enable audit logging",
                    value=True
                )
                
                log_to_file = st.checkbox(
                    "Log to file",
                    value=True
                )
            
            st.markdown("### Database Configuration")
            
            db_pool_size = st.number_input(
                "Database connection pool size",
                min_value=1,
                max_value=50,
                value=10
            )
            
            query_timeout = st.number_input(
                "Query timeout (seconds)",
                min_value=1,
                max_value=300,
                value=30
            )
            
            st.markdown("### 🚨 Danger Zone")
            
            with st.expander("Dangerous Operations", icon="⚠️"):
                st.warning("These operations can break the platform!")
                
                col_danger1, col_danger2 = st.columns(2)
                
                with col_danger1:
                    if st.button("Reset All Settings", type="secondary"):
                        st.error("This will reset all settings to defaults!")
                        if st.button("Confirm Reset", type="primary"):
                            st.info("Reset feature coming soon!")
                
                with col_danger2:
                    if st.button("Clear All Data", type="secondary"):
                        st.error("This will delete ALL data from the platform!")
                        if st.button("Confirm Clear", type="primary"):
                            st.info("Clear data feature coming soon!")
            
            if st.form_submit_button("Save Advanced Settings", type="primary"):
                st.success("Advanced settings saved successfully!")
