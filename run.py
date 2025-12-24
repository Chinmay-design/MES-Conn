#!/usr/bin/env python3
"""
MES-Connect Application Runner
"""

import subprocess
import sys
import os
import webbrowser
from threading import Timer
import socket

def check_port_available(port):
    """Check if port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists("data"):
        os.makedirs("data")
        print("✅ Created data directory")

def setup_database():
    """Initialize database"""
    print("🗄️ Setting up database...")
    try:
        # Import and create tables
        from utils.database import create_tables
        create_tables()
        print("✅ Database setup completed!")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def open_browser(port):
    """Open browser after delay"""
    def open():
        webbrowser.open_new(f"http://localhost:{port}")
    
    Timer(2.0, open).start()

def run_application():
    """Run the Streamlit application"""
    port = 8501
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️ Port {port} is already in use. Trying alternative port...")
        port = 8502
        if not check_port_available(port):
            print(f"❌ Port {port} is also in use. Please close other applications and try again.")
            return False
    
    print(f"🚀 Starting MES-Connect on port {port}...")
    print("👉 Opening browser automatically...")
    
    # Open browser
    open_browser(port)
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
        return True
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

def create_admin_account():
    """Create an admin account"""
    print("👑 Creating admin account...")
    
    try:
        from utils.database import add_user
        
        # Check if admin already exists
        import sqlite3
        conn = sqlite3.connect("data/mes_connect.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE role = 'admin'")
        if cursor.fetchone():
            print("✅ Admin account already exists")
            conn.close()
            return True
        
        # Create admin account
        admin_id = add_user(
            email="admin@mes.edu",
            password="Admin123",  # Change this in production!
            role="admin",
            first_name="System",
            last_name="Administrator",
            student_id="ADMIN001",
            department="Administration",
            year="2024",
            is_verified=1
        )
        
        if admin_id:
            print("✅ Admin account created successfully!")
            print("📧 Email: admin@mes.edu")
            print("🔑 Password: Admin123")
            print("⚠️  Change this password immediately after first login!")
            return True
        else:
            print("❌ Failed to create admin account")
            return False
    except Exception as e:
        print(f"❌ Error creating admin account: {e}")
        return False

def main():
    """Main runner function"""
    print("\n" + "="*50)
    print("🎓 MES-Connect Platform Setup")
    print("="*50)
    
    # Create data directory
    create_data_directory()
    
    # Ask for setup options
    print("\n📋 Setup Options:")
    print("1. Full setup (install requirements + create admin)")
    print("2. Install requirements only")
    print("3. Create admin account only")
    print("4. Just run the application")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
        sys.exit(0)
    
    # Process choice
    if choice == "1":
        # Full setup
        if not install_requirements():
            sys.exit(1)
        if not setup_database():
            sys.exit(1)
        create_admin_account()
    elif choice == "2":
        # Install requirements only
        if not install_requirements():
            sys.exit(1)
    elif choice == "3":
        # Create admin only
        create_admin_account()
    elif choice == "4":
        # Just run
        pass
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    # Run application
    print("\n" + "="*50)
    print("🚀 Starting MES-Connect Application")
    print("="*50)
    print("\n📱 Application will open in your browser automatically")
    print("🛑 Press Ctrl+C to stop the application\n")
    
    run_application()

if __name__ == "__main__":
    main()
