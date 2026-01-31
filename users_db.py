"""
Database module for user management
Stores user credentials in JSON (can be upgraded to SQL later)
"""

import json
import os
from typing import Optional, Dict, List
from datetime import datetime
from threading import Lock

# Database file for users
USERS_DB_FILE = os.path.join(os.path.dirname(__file__), 'users_store.json')
users_lock = Lock()

# In-memory cache
_users_cache: Dict[str, dict] = {}
_user_id_counter = 0


def _load_users_db():
    """Load users from JSON file"""
    global _users_cache, _user_id_counter
    
    if not os.path.exists(USERS_DB_FILE):
        return
    
    try:
        with open(USERS_DB_FILE, 'r') as f:
            data = json.load(f)
            _users_cache = {u['user_id']: u for u in data.get('users', [])}
            _user_id_counter = data.get('next_user_id', len(_users_cache) + 1)
    except Exception as e:
        print(f"Error loading users DB: {e}")


def _save_users_db():
    """Save users to JSON file"""
    global _users_cache
    
    try:
        with open(USERS_DB_FILE, 'w') as f:
            data = {
                'users': list(_users_cache.values()),
                'next_user_id': max([int(uid) for uid in _users_cache.keys()], default=0) + 1,
                'updated_at': datetime.now().isoformat()
            }
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving users DB: {e}")


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    with users_lock:
        for user in _users_cache.values():
            if user.get('username') == username:
                return user
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    with users_lock:
        return _users_cache.get(str(user_id))


def get_user_by_student_id(student_id: str) -> Optional[dict]:
    """Get user by student ID (for students)"""
    with users_lock:
        for user in _users_cache.values():
            if user.get('student_id') == student_id and user.get('role') == 'student':
                return user
    return None


def create_user(username: str, password_hash: str, email: str, role: str, 
                name: str, student_id: Optional[str] = None) -> dict:
    """Create a new user"""
    global _user_id_counter
    
    with users_lock:
        _user_id_counter += 1
        user_id = _user_id_counter
        
        user = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'email': email,
            'role': role,
            'name': name,
            'student_id': student_id,
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        _users_cache[str(user_id)] = user
        _save_users_db()
        
        return user


def user_exists(username: str) -> bool:
    """Check if username already exists"""
    return get_user_by_username(username) is not None


def get_all_users() -> List[dict]:
    """Get all users (for admin)"""
    with users_lock:
        return list(_users_cache.values())


def get_all_students() -> List[dict]:
    """Get all student users"""
    with users_lock:
        return [u for u in _users_cache.values() if u.get('role') == 'student']


# Load users on module import
_load_users_db()
