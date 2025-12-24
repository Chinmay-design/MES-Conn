import sqlite3
import bcrypt
from datetime import datetime
import json
from typing import Optional, List, Dict, Any

DATABASE_PATH = "data/mes_connect.db"

def get_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create all necessary tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'alumni', 'admin')),
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        student_id TEXT,
        department TEXT,
        year TEXT,
        skills TEXT,
        about TEXT,
        current_position TEXT,
        company TEXT,
        linkedin TEXT,
        profile_pic TEXT,
        is_verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    # Friends table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        friend_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'blocked')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (friend_id) REFERENCES users (id),
        UNIQUE(user_id, friend_id)
    )
    ''')
    
    # Messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (receiver_id) REFERENCES users (id)
    )
    ''')
    
    # Groups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_by INTEGER NOT NULL,
        is_public INTEGER DEFAULT 1,
        category TEXT DEFAULT 'general',
        cover_pic TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    # Group members table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT DEFAULT 'member' CHECK(role IN ('admin', 'moderator', 'member')),
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(group_id, user_id)
    )
    ''')
    
    # Group messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        sender_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        attachment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (id),
        FOREIGN KEY (sender_id) REFERENCES users (id)
    )
    ''')
    
    # Confessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS confessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT NOT NULL,
        is_anonymous INTEGER DEFAULT 1,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
        likes INTEGER DEFAULT 0,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Confession likes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS confession_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        confession_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (confession_id) REFERENCES confessions (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(confession_id, user_id)
    )
    ''')
    
    # Events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        organizer_id INTEGER NOT NULL,
        event_date DATE NOT NULL,
        event_time TIME,
        location TEXT,
        venue TEXT,
        max_participants INTEGER,
        is_public INTEGER DEFAULT 1,
        category TEXT DEFAULT 'general',
        cover_pic TEXT,
        registration_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (organizer_id) REFERENCES users (id)
    )
    ''')
    
    # Event participants table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT DEFAULT 'registered' CHECK(status IN ('registered', 'attended', 'cancelled')),
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(event_id, user_id)
    )
    ''')
    
    # Announcements table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        target_role TEXT,
        priority TEXT DEFAULT 'normal' CHECK(priority IN ('low', 'normal', 'high', 'urgent')),
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    # Contributions table (for alumni)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumni_id INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('mentorship', 'donation', 'workshop', 'job_posting', 'internship', 'other')),
        title TEXT NOT NULL,
        description TEXT,
        amount REAL,
        hours INTEGER,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'completed', 'rejected')),
        skills_required TEXT,
        deadline DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (alumni_id) REFERENCES users (id)
    )
    ''')
    
    # Notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT CHECK(type IN ('friend_request', 'message', 'event', 'confession', 'announcement', 'system')),
        is_read INTEGER DEFAULT 0,
        reference_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Job postings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_postings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        posted_by INTEGER NOT NULL,
        company TEXT NOT NULL,
        position TEXT NOT NULL,
        description TEXT NOT NULL,
        requirements TEXT,
        location TEXT,
        salary_range TEXT,
        job_type TEXT CHECK(job_type IN ('full_time', 'part_time', 'internship', 'contract')),
        application_link TEXT,
        is_active INTEGER DEFAULT 1,
        deadline DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (posted_by) REFERENCES users (id)
    )
    ''')
    
    # Job applications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        applicant_id INTEGER NOT NULL,
        cover_letter TEXT,
        resume TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'reviewed', 'accepted', 'rejected')),
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES job_postings (id),
        FOREIGN KEY (applicant_id) REFERENCES users (id),
        UNIQUE(job_id, applicant_id)
    )
    ''')
    
    # Resources table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uploaded_by INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        file_path TEXT NOT NULL,
        file_type TEXT,
        category TEXT,
        tags TEXT,
        download_count INTEGER DEFAULT 0,
        is_public INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uploaded_by) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password: str, password: str) -> bool:
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# User Management Functions
def add_user(email: str, password: str, role: str, **kwargs) -> Optional[int]:
    """Add a new user to database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        hashed_pw = hash_password(password)
        
        user_data = {
            'email': email,
            'password': hashed_pw,
            'role': role,
            'first_name': kwargs.get('first_name', ''),
            'last_name': kwargs.get('last_name', ''),
            'phone': kwargs.get('phone', ''),
            'student_id': kwargs.get('student_id', ''),
            'department': kwargs.get('department', ''),
            'year': kwargs.get('year', ''),
            'skills': kwargs.get('skills', ''),
            'about': kwargs.get('about', ''),
            'current_position': kwargs.get('current_position', ''),
            'company': kwargs.get('company', ''),
            'linkedin': kwargs.get('linkedin', ''),
            'profile_pic': kwargs.get('profile_pic', ''),
            'is_verified': 1 if role == 'admin' else 0
        }
        
        columns = ', '.join(user_data.keys())
        placeholders = ', '.join(['?'] * len(user_data))
        
        cursor.execute(f'''
            INSERT INTO users ({columns}) 
            VALUES ({placeholders})
        ''', list(user_data.values()))
        
        user_id = cursor.lastrowid
        
        # Create welcome notification
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, 'Welcome to MES-Connect!', 'Your account has been created successfully.', 'system')
        ''', (user_id,))
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        raise Exception(f"Email already exists: {email}")
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()

def verify_user(email: str, password: str) -> Optional[int]:
    """Verify user credentials"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, password FROM users 
            WHERE email = ? AND is_verified = 1
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user and check_password(user['password'], password):
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user['id'],))
            conn.commit()
            return user['id']
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, first_name, last_name, email, role, department, 
                   year, current_position, company, profile_pic, 
                   skills, about, phone, student_id, linkedin,
                   created_at, last_login
            FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()

def get_user_role(user_id: int) -> Optional[str]:
    """Get user role"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        return result['role'] if result else None
    finally:
        conn.close()

def get_student_profile(user_id: int) -> Optional[Dict]:
    """Get student profile"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, first_name, last_name, email, phone, student_id,
                   department, year, skills, about, profile_pic, created_at,
                   last_login
            FROM users WHERE id = ? AND role = 'student'
        ''', (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()

def get_alumni_profile(user_id: int) -> Optional[Dict]:
    """Get alumni profile"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, first_name, last_name, email, phone, student_id as roll_number,
                   department, year as graduation_year, skills, about, 
                   current_position, company, linkedin, profile_pic, 
                   created_at, last_login
            FROM users WHERE id = ? AND role = 'alumni'
        ''', (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()

def update_user_profile(user_id: int, **kwargs) -> bool:
    """Update user profile"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        update_fields = []
        values = []
        
        for key, value in kwargs.items():
            if value is not None:
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        if update_fields:
            values.append(user_id)
            query = f'''
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = ?
            '''
            cursor.execute(query, values)
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False
    finally:
        conn.close()

def get_all_users(role: Optional[str] = None, exclude_id: Optional[int] = None) -> List[Dict]:
    """Get all users, optionally filtered by role"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, first_name, last_name, email, role, department, 
                   year, current_position, company, profile_pic,
                   skills, about, created_at
            FROM users 
            WHERE is_verified = 1
        '''
        params = []
        
        if role:
            query += ' AND role = ?'
            params.append(role)
        
        if exclude_id:
            query += ' AND id != ?'
            params.append(exclude_id)
        
        query += ' ORDER BY first_name, last_name'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# Friends Management Functions
def get_friends(user_id: int, status: str = 'accepted') -> List[Dict]:
    """Get friends list"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, u.email, u.role,
                   u.department, u.current_position, u.company, u.profile_pic,
                   f.created_at as friends_since,
                   CASE 
                     WHEN f.user_id = ? THEN 'outgoing'
                     ELSE 'incoming'
                   END as request_direction
            FROM friends f
            JOIN users u ON (f.friend_id = u.id AND f.user_id = ?) 
                        OR (f.user_id = u.id AND f.friend_id = ?)
            WHERE (f.user_id = ? OR f.friend_id = ?) 
              AND u.id != ?
              AND f.status = ?
            ORDER BY u.first_name, u.last_name
        ''', (user_id, user_id, user_id, user_id, user_id, user_id, status))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def add_friend_request(user_id: int, friend_id: int) -> tuple[bool, str]:
    """Send friend request"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if request already exists
        cursor.execute('''
            SELECT id, status FROM friends 
            WHERE ((user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?))
        ''', (user_id, friend_id, friend_id, user_id))
        
        existing = cursor.fetchone()
        if existing:
            if existing['status'] == 'pending':
                return False, "Friend request already pending"
            elif existing['status'] == 'accepted':
                return False, "Already friends"
            elif existing['status'] == 'blocked':
                return False, "Cannot send request to blocked user"
        
        cursor.execute('''
            INSERT INTO friends (user_id, friend_id, status)
            VALUES (?, ?, 'pending')
        ''', (user_id, friend_id))
        
        # Create notification
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            VALUES (?, 'New Friend Request', 
                   (SELECT first_name || ' ' || last_name FROM users WHERE id = ?) || ' sent you a friend request',
                   'friend_request', ?)
        ''', (friend_id, user_id, cursor.lastrowid))
        
        conn.commit()
        return True, "Friend request sent"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_pending_friend_requests(user_id: int) -> List[Dict]:
    """Get pending friend requests"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.id as request_id, u.id as user_id, u.first_name, u.last_name,
                   u.email, u.role, u.department, u.profile_pic, u.current_position,
                   u.company, f.created_at
            FROM friends f
            JOIN users u ON f.user_id = u.id
            WHERE f.friend_id = ? AND f.status = 'pending'
            ORDER BY f.created_at DESC
        ''', (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def accept_friend_request(request_id: int, user_id: int) -> bool:
    """Accept friend request"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get request details
        cursor.execute('''
            SELECT user_id, friend_id FROM friends 
            WHERE id = ? AND friend_id = ?
        ''', (request_id, user_id))
        
        request = cursor.fetchone()
        if not request:
            return False
        
        # Update status
        cursor.execute('''
            UPDATE friends 
            SET status = 'accepted'
            WHERE id = ?
        ''', (request_id,))
        
        # Create notification for requester
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            VALUES (?, 'Friend Request Accepted', 
                   (SELECT first_name || ' ' || last_name FROM users WHERE id = ?) || ' accepted your friend request',
                   'friend_request', ?)
        ''', (request['user_id'], user_id, request_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error accepting friend request: {e}")
        return False
    finally:
        conn.close()

def reject_friend_request(request_id: int, user_id: int) -> bool:
    """Reject friend request"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM friends 
            WHERE id = ? AND friend_id = ?
        ''', (request_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def remove_friend(user_id: int, friend_id: int) -> bool:
    """Remove friend"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM friends 
            WHERE (user_id = ? AND friend_id = ?) 
               OR (user_id = ? AND friend_id = ?)
        ''', (user_id, friend_id, friend_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Chat Functions
def get_chat_messages(user_id: int, other_user_id: int, limit: int = 50) -> List[Dict]:
    """Get chat messages between two users"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, 
                   s.first_name as sender_first_name,
                   s.last_name as sender_last_name,
                   s.profile_pic as sender_profile_pic,
                   r.first_name as receiver_first_name,
                   r.last_name as receiver_last_name
            FROM messages m
            JOIN users s ON m.sender_id = s.id
            JOIN users r ON m.receiver_id = r.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?)
               OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.created_at DESC
            LIMIT ?
        ''', (user_id, other_user_id, other_user_id, user_id, limit))
        
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Mark messages as read
        cursor.execute('''
            UPDATE messages 
            SET is_read = 1 
            WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
        ''', (user_id, other_user_id))
        conn.commit()
        
        return messages[::-1]  # Reverse to show oldest first
    finally:
        conn.close()

def send_message(sender_id: int, receiver_id: int, message: str) -> Optional[int]:
    """Send a message"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (sender_id, receiver_id, message)
            VALUES (?, ?, ?)
        ''', (sender_id, receiver_id, message))
        
        message_id = cursor.lastrowid
        
        # Create notification
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            VALUES (?, 'New Message', 
                   (SELECT first_name || ' ' || last_name FROM users WHERE id = ?) || ' sent you a message',
                   'message', ?)
        ''', (receiver_id, sender_id, message_id))
        
        conn.commit()
        return message_id
    except Exception as e:
        print(f"Error sending message: {e}")
        return None
    finally:
        conn.close()

def get_conversations(user_id: int) -> List[Dict]:
    """Get all conversations for a user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                other_user.id as user_id,
                other_user.first_name,
                other_user.last_name,
                other_user.profile_pic,
                other_user.role,
                other_user.department,
                last_msg.message as last_message,
                last_msg.created_at as last_message_time,
                SUM(CASE WHEN m.is_read = 0 AND m.receiver_id = ? THEN 1 ELSE 0 END) as unread_count
            FROM (
                SELECT DISTINCT 
                    CASE 
                        WHEN sender_id = ? THEN receiver_id
                        ELSE sender_id
                    END as other_user_id
                FROM messages
                WHERE sender_id = ? OR receiver_id = ?
            ) as conversations
            JOIN users other_user ON conversations.other_user_id = other_user.id
            LEFT JOIN messages last_msg ON last_msg.id = (
                SELECT id FROM messages
                WHERE (sender_id = ? AND receiver_id = other_user.id)
                   OR (sender_id = other_user.id AND receiver_id = ?)
                ORDER BY created_at DESC
                LIMIT 1
            )
            LEFT JOIN messages m ON (m.sender_id = other_user.id AND m.receiver_id = ? AND m.is_read = 0)
            GROUP BY other_user.id
            ORDER BY last_msg.created_at DESC
        ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# Groups Functions
def create_group(name: str, description: str, created_by: int, **kwargs) -> Optional[int]:
    """Create a new group"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO groups (name, description, created_by, is_public, category, cover_pic)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, created_by, 
              kwargs.get('is_public', 1),
              kwargs.get('category', 'general'),
              kwargs.get('cover_pic')))
        
        group_id = cursor.lastrowid
        
        # Add creator as admin
        cursor.execute('''
            INSERT INTO group_members (group_id, user_id, role)
            VALUES (?, ?, 'admin')
        ''', (group_id, created_by))
        
        conn.commit()
        return group_id
    except Exception as e:
        print(f"Error creating group: {e}")
        return None
    finally:
        conn.close()

def get_groups(user_id: Optional[int] = None, category: Optional[str] = None) -> List[Dict]:
    """Get groups, optionally filtered by user membership or category"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT g.*, 
                       u.first_name as creator_first_name,
                       u.last_name as creator_last_name,
                       COUNT(gm.user_id) as member_count,
                       gm.role as user_role
                FROM groups g
                JOIN users u ON g.created_by = u.id
                LEFT JOIN group_members gm ON g.id = gm.group_id
                WHERE gm.user_id = ? OR g.is_public = 1
                GROUP BY g.id
                ORDER BY g.created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT g.*, 
                       u.first_name as creator_first_name,
                       u.last_name as creator_last_name,
                       COUNT(gm.user_id) as member_count
                FROM groups g
                JOIN users u ON g.created_by = u.id
                LEFT JOIN group_members gm ON g.id = gm.group_id
                GROUP BY g.id
                ORDER BY g.created_at DESC
            ''')
        
        groups = [dict(row) for row in cursor.fetchall()]
        
        if category:
            groups = [g for g in groups if g['category'] == category]
        
        return groups
    finally:
        conn.close()

def join_group(group_id: int, user_id: int) -> bool:
    """Join a group"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if already a member
        cursor.execute('''
            SELECT id FROM group_members 
            WHERE group_id = ? AND user_id = ?
        ''', (group_id, user_id))
        
        if cursor.fetchone():
            return False
        
        cursor.execute('''
            INSERT INTO group_members (group_id, user_id)
            VALUES (?, ?)
        ''', (group_id, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error joining group: {e}")
        return False
    finally:
        conn.close()

def get_group_members(group_id: int) -> List[Dict]:
    """Get all members of a group"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.first_name, u.last_name, u.email, u.role,
                   u.department, u.profile_pic, u.current_position, u.company,
                   gm.role as group_role, gm.joined_at
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = ?
            ORDER BY 
                CASE gm.role 
                    WHEN 'admin' THEN 1
                    WHEN 'moderator' THEN 2
                    ELSE 3
                END,
                gm.joined_at
        ''', (group_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_group_messages(group_id: int, limit: int = 50) -> List[Dict]:
    """Get messages from a group"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gm.*, 
                   u.first_name, u.last_name, u.profile_pic, u.role
            FROM group_messages gm
            JOIN users u ON gm.sender_id = u.id
            WHERE gm.group_id = ?
            ORDER BY gm.created_at DESC
            LIMIT ?
        ''', (group_id, limit))
        
        messages = [dict(row) for row in cursor.fetchall()]
        return messages[::-1]  # Reverse to show oldest first
    finally:
        conn.close()

def send_group_message(group_id: int, sender_id: int, message: str, attachment: Optional[str] = None) -> Optional[int]:
    """Send a message to a group"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO group_messages (group_id, sender_id, message, attachment)
            VALUES (?, ?, ?, ?)
        ''', (group_id, sender_id, message, attachment))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error sending group message: {e}")
        return None
    finally:
        conn.close()

# Confessions Functions
def add_confession(user_id: Optional[int], content: str, is_anonymous: bool = True, tags: Optional[str] = None) -> Optional[int]:
    """Add a confession"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO confessions (user_id, content, is_anonymous, tags, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (None if is_anonymous else user_id, content, 1 if is_anonymous else 0, tags))
        
        confession_id = cursor.lastrowid
        
        # Create notification for admins
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            SELECT id, 'New Confession Pending', 'A new confession needs moderation', 'confession', ?
            FROM users WHERE role = 'admin'
        ''', (confession_id,))
        
        conn.commit()
        return confession_id
    except Exception as e:
        print(f"Error adding confession: {e}")
        return None
    finally:
        conn.close()

def get_confessions(status: str = 'approved', limit: int = 50, offset: int = 0) -> List[Dict]:
    """Get confessions"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if status == 'all':
            cursor.execute('''
                SELECT c.*, 
                       u.first_name, u.last_name, u.profile_pic,
                       (SELECT COUNT(*) FROM confession_likes WHERE confession_id = c.id) as like_count,
                       (SELECT COUNT(*) FROM confession_likes WHERE confession_id = c.id AND user_id = ?) as user_liked
                FROM confessions c
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.created_at DESC
                LIMIT ? OFFSET ?
            ''', (None, limit, offset))
        else:
            cursor.execute('''
                SELECT c.*, 
                       u.first_name, u.last_name, u.profile_pic,
                       (SELECT COUNT(*) FROM confession_likes WHERE confession_id = c.id) as like_count,
                       (SELECT COUNT(*) FROM confession_likes WHERE confession_id = c.id AND user_id = ?) as user_liked
                FROM confessions c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.status = ?
                ORDER BY c.created_at DESC
                LIMIT ? OFFSET ?
            ''', (None, status, limit, offset))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def like_confession(confession_id: int, user_id: int) -> bool:
    """Like or unlike a confession"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if already liked
        cursor.execute('''
            SELECT id FROM confession_likes 
            WHERE confession_id = ? AND user_id = ?
        ''', (confession_id, user_id))
        
        if cursor.fetchone():
            # Unlike
            cursor.execute('''
                DELETE FROM confession_likes 
                WHERE confession_id = ? AND user_id = ?
            ''', (confession_id, user_id))
        else:
            # Like
            cursor.execute('''
                INSERT INTO confession_likes (confession_id, user_id)
                VALUES (?, ?)
            ''', (confession_id, user_id))
        
        # Update like count
        cursor.execute('''
            UPDATE confessions 
            SET likes = (SELECT COUNT(*) FROM confession_likes WHERE confession_id = ?)
            WHERE id = ?
        ''', (confession_id, confession_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error liking confession: {e}")
        return False
    finally:
        conn.close()

def update_confession_status(confession_id: int, status: str) -> bool:
    """Update confession status (for moderation)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE confessions 
            SET status = ?
            WHERE id = ?
        ''', (status, confession_id))
        
        # Create notification for confession owner if not anonymous
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            SELECT user_id, 
                   CASE 
                     WHEN ? = 'approved' THEN 'Confession Approved'
                     ELSE 'Confession Rejected'
                   END,
                   CASE 
                     WHEN ? = 'approved' THEN 'Your confession has been approved and is now visible'
                     ELSE 'Your confession has been rejected'
                   END,
                   'confession', ?
            FROM confessions 
            WHERE id = ? AND user_id IS NOT NULL
        ''', (status, status, confession_id, confession_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating confession status: {e}")
        return False
    finally:
        conn.close()

# Events Functions
def add_event(title: str, description: str, organizer_id: int, event_date: str, **kwargs) -> Optional[int]:
    """Add an event"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (title, description, organizer_id, event_date, 
                              event_time, location, venue, max_participants, 
                              is_public, category, cover_pic, registration_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, organizer_id, event_date,
              kwargs.get('event_time'), kwargs.get('location'),
              kwargs.get('venue'), kwargs.get('max_participants'),
              kwargs.get('is_public', 1), kwargs.get('category', 'general'),
              kwargs.get('cover_pic'), kwargs.get('registration_link')))
        
        event_id = cursor.lastrowid
        
        # Auto-register organizer
        cursor.execute('''
            INSERT INTO event_participants (event_id, user_id, status)
            VALUES (?, ?, 'registered')
        ''', (event_id, organizer_id))
        
        conn.commit()
        return event_id
    except Exception as e:
        print(f"Error adding event: {e}")
        return None
    finally:
        conn.close()

def get_events(upcoming: bool = True, limit: int = 20, user_id: Optional[int] = None) -> List[Dict]:
    """Get events"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if upcoming:
            date_filter = "e.event_date >= DATE('now')"
        else:
            date_filter = "e.event_date < DATE('now')"
        
        if user_id:
            cursor.execute(f'''
                SELECT e.*, 
                       u.first_name as organizer_first_name,
                       u.last_name as organizer_last_name,
                       u.profile_pic as organizer_profile_pic,
                       COUNT(ep.id) as participant_count,
                       MAX(CASE WHEN ep.user_id = ? THEN 1 ELSE 0 END) as is_registered
                FROM events e
                JOIN users u ON e.organizer_id = u.id
                LEFT JOIN event_participants ep ON e.id = ep.event_id
                WHERE {date_filter}
                GROUP BY e.id
                ORDER BY e.event_date, e.event_time
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute(f'''
                SELECT e.*, 
                       u.first_name as organizer_first_name,
                       u.last_name as organizer_last_name,
                       u.profile_pic as organizer_profile_pic,
                       COUNT(ep.id) as participant_count
                FROM events e
                JOIN users u ON e.organizer_id = u.id
                LEFT JOIN event_participants ep ON e.id = ep.event_id
                WHERE {date_filter}
                GROUP BY e.id
                ORDER BY e.event_date, e.event_time
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def register_for_event(event_id: int, user_id: int) -> tuple[bool, str]:
    """Register user for an event"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if already registered
        cursor.execute('''
            SELECT id FROM event_participants 
            WHERE event_id = ? AND user_id = ?
        ''', (event_id, user_id))
        
        if cursor.fetchone():
            return False, "Already registered"
        
        # Check if event is full
        cursor.execute('''
            SELECT e.max_participants, COUNT(ep.id) as current_participants
            FROM events e
            LEFT JOIN event_participants ep ON e.id = ep.event_id
            WHERE e.id = ?
            GROUP BY e.id
        ''', (event_id,))
        
        event_info = cursor.fetchone()
        if event_info and event_info['max_participants']:
            if event_info['current_participants'] >= event_info['max_participants']:
                return False, "Event is full"
        
        cursor.execute('''
            INSERT INTO event_participants (event_id, user_id)
            VALUES (?, ?)
        ''', (event_id, user_id))
        
        # Create notification
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            VALUES (?, 'Event Registration', 
                   'You have successfully registered for an event',
                   'event', ?)
        ''', (user_id, event_id))
        
        conn.commit()
        return True, "Successfully registered"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_events(user_id: int, upcoming: bool = True) -> List[Dict]:
    """Get events user is registered for"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if upcoming:
            date_filter = "e.event_date >= DATE('now')"
        else:
            date_filter = "e.event_date < DATE('now')"
        
        cursor.execute(f'''
            SELECT e.*, 
                   u.first_name as organizer_first_name,
                   u.last_name as organizer_last_name,
                   ep.status, ep.registered_at
            FROM event_participants ep
            JOIN events e ON ep.event_id = e.id
            JOIN users u ON e.organizer_id = u.id
            WHERE ep.user_id = ? AND {date_filter}
            ORDER BY e.event_date, e.event_time
        ''', (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# Announcements Functions
def add_announcement(title: str, content: str, created_by: int, target_role: Optional[str] = None, priority: str = 'normal') -> Optional[int]:
    """Add an announcement"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO announcements (title, content, created_by, target_role, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, created_by, target_role, priority))
        
        announcement_id = cursor.lastrowid
        
        # Create notifications for targeted users
        if target_role and target_role != 'all':
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, reference_id)
                SELECT id, 'New Announcement', ?, 'announcement', ?
                FROM users 
                WHERE role = ? AND is_verified = 1
            ''', (title, announcement_id, target_role))
        else:
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, reference_id)
                SELECT id, 'New Announcement', ?, 'announcement', ?
                FROM users 
                WHERE is_verified = 1
            ''', (title, announcement_id))
        
        conn.commit()
        return announcement_id
    except Exception as e:
        print(f"Error adding announcement: {e}")
        return None
    finally:
        conn.close()

def get_announcements(target_role: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """Get announcements"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if target_role:
            cursor.execute('''
                SELECT a.*, 
                       u.first_name, u.last_name, u.profile_pic
                FROM announcements a
                JOIN users u ON a.created_by = u.id
                WHERE a.is_active = 1 
                AND (a.target_role = ? OR a.target_role = 'all' OR a.target_role IS NULL)
                ORDER BY 
                    CASE a.priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'normal' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    a.created_at DESC
                LIMIT ?
            ''', (target_role, limit))
        else:
            cursor.execute('''
                SELECT a.*, 
                       u.first_name, u.last_name, u.profile_pic
                FROM announcements a
                JOIN users u ON a.created_by = u.id
                WHERE a.is_active = 1
                ORDER BY 
                    CASE a.priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'normal' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    a.created_at DESC
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# Contributions Functions (Alumni)
def add_contribution(alumni_id: int, type: str, title: str, **kwargs) -> Optional[int]:
    """Add a contribution"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contributions (alumni_id, type, title, description, 
                                     amount, hours, status, skills_required, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (alumni_id, type, title, 
              kwargs.get('description'),
              kwargs.get('amount'),
              kwargs.get('hours'),
              kwargs.get('status', 'pending'),
              kwargs.get('skills_required'),
              kwargs.get('deadline')))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error adding contribution: {e}")
        return None
    finally:
        conn.close()

def get_contributions(alumni_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:
    """Get contributions"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT c.*, 
                   u.first_name, u.last_name, u.profile_pic,
                   u.current_position, u.company
            FROM contributions c
            JOIN users u ON c.alumni_id = u.id
        '''
        params = []
        
        if alumni_id:
            query += ' WHERE c.alumni_id = ?'
            params.append(alumni_id)
        
        if status:
            if alumni_id:
                query += ' AND c.status = ?'
            else:
                query += ' WHERE c.status = ?'
            params.append(status)
        
        query += ' ORDER BY c.created_at DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# Notifications Functions
def get_notifications(user_id: int, unread_only: bool = False, limit: int = 20) -> List[Dict]:
    """Get notifications for a user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if unread_only:
            cursor.execute('''
                SELECT * FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def mark_notification_read(notification_id: int) -> bool:
    """Mark a notification as read"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE id = ?
        ''', (notification_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def mark_all_notifications_read(user_id: int) -> bool:
    """Mark all notifications as read for a user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Job Postings Functions
def add_job_posting(posted_by: int, company: str, position: str, description: str, **kwargs) -> Optional[int]:
    """Add a job posting"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_postings (posted_by, company, position, description,
                                     requirements, location, salary_range, 
                                     job_type, application_link, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (posted_by, company, position, description,
              kwargs.get('requirements'),
              kwargs.get('location'),
              kwargs.get('salary_range'),
              kwargs.get('job_type', 'full_time'),
              kwargs.get('application_link'),
              kwargs.get('deadline')))
        
        job_id = cursor.lastrowid
        
        # Create notification for students
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            SELECT id, 'New Job Opportunity', ?, 'announcement', ?
            FROM users 
            WHERE role = 'student' AND is_verified = 1
        ''', (f"New position: {position} at {company}", job_id))
        
        conn.commit()
        return job_id
    except Exception as e:
        print(f"Error adding job posting: {e}")
        return None
    finally:
        conn.close()

def get_job_postings(active_only: bool = True, limit: int = 20) -> List[Dict]:
    """Get job postings"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('''
                SELECT j.*, 
                       u.first_name, u.last_name, u.profile_pic,
                       u.current_position, u.company as poster_company
                FROM job_postings j
                JOIN users u ON j.posted_by = u.id
                WHERE j.is_active = 1 
                AND (j.deadline IS NULL OR j.deadline >= DATE('now'))
                ORDER BY j.created_at DESC
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT j.*, 
                       u.first_name, u.last_name, u.profile_pic,
                       u.current_position, u.company as poster_company
                FROM job_postings j
                JOIN users u ON j.posted_by = u.id
                ORDER BY j.created_at DESC
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def apply_for_job(job_id: int, applicant_id: int, cover_letter: Optional[str] = None, resume: Optional[str] = None) -> bool:
    """Apply for a job"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if already applied
        cursor.execute('''
            SELECT id FROM job_applications 
            WHERE job_id = ? AND applicant_id = ?
        ''', (job_id, applicant_id))
        
        if cursor.fetchone():
            return False
        
        cursor.execute('''
            INSERT INTO job_applications (job_id, applicant_id, cover_letter, resume)
            VALUES (?, ?, ?, ?)
        ''', (job_id, applicant_id, cover_letter, resume))
        
        # Create notification for job poster
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, reference_id)
            SELECT posted_by, 'New Job Application', 
                   (SELECT first_name || ' ' || last_name FROM users WHERE id = ?) || ' applied for ' || position,
                   'announcement', ?
            FROM job_postings 
            WHERE id = ?
        ''', (applicant_id, cursor.lastrowid, job_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error applying for job: {e}")
        return False
    finally:
        conn.close()

# Analytics Functions
def get_user_statistics() -> Dict:
    """Get user statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total users
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_verified = 1")
        stats['total_users'] = cursor.fetchone()['total']
        
        # Users by role
        cursor.execute('''
            SELECT role, COUNT(*) as count 
            FROM users 
            WHERE is_verified = 1 
            GROUP BY role
        ''')
        stats['users_by_role'] = {row['role']: row['count'] for row in cursor.fetchall()}
        
        # Users by department
        cursor.execute('''
            SELECT department, COUNT(*) as count 
            FROM users 
            WHERE is_verified = 1 AND department IS NOT NULL
            GROUP BY department
        ''')
        stats['users_by_department'] = {row['department']: row['count'] for row in cursor.fetchall()}
        
        # New users this month
        cursor.execute('''
            SELECT COUNT(*) as count FROM users 
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
            AND is_verified = 1
        ''')
        stats['new_users_month'] = cursor.fetchone()['count']
        
        # Active users (logged in last 30 days)
        cursor.execute('''
            SELECT COUNT(*) as count FROM users 
            WHERE last_login >= DATE('now', '-30 days')
            AND is_verified = 1
        ''')
        stats['active_users'] = cursor.fetchone()['count']
        
        return stats
    finally:
        conn.close()

def get_platform_statistics() -> Dict:
    """Get platform statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total confessions
        cursor.execute("SELECT COUNT(*) as total FROM confessions WHERE status = 'approved'")
        stats['total_confessions'] = cursor.fetchone()['total']
        
        # Total events
        cursor.execute("SELECT COUNT(*) as total FROM events WHERE event_date >= DATE('now')")
        stats['active_events'] = cursor.fetchone()['total']
        
        # Total groups
        cursor.execute("SELECT COUNT(*) as total FROM groups")
        stats['total_groups'] = cursor.fetchone()['total']
        
        # Total messages
        cursor.execute("SELECT COUNT(*) as total FROM messages")
        stats['total_messages'] = cursor.fetchone()['total']
        
        # Total job postings
        cursor.execute("SELECT COUNT(*) as total FROM job_postings WHERE is_active = 1")
        stats['active_jobs'] = cursor.fetchone()['total']
        
        return stats
    finally:
        conn.close()

def get_growth_data(days: int = 30) -> List[Dict]:
    """Get growth data for chart"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as new_users,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as students,
                SUM(CASE WHEN role = 'alumni' THEN 1 ELSE 0 END) as alumni
            FROM users 
            WHERE is_verified = 1
            AND DATE(created_at) >= DATE('now', '-{days} days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
