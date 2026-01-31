"""
Authentication module for user login/signup
Handles JWT tokens, password hashing, and role-based access
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import BaseModel, validator
from jose import JWTError, jwt
import os
import hashlib
import secrets

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# ==================== MODELS ====================

class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    username: str
    role: str  # admin, teacher, student


class LoginRequest(BaseModel):
    """Login request payload"""
    username: str
    password: str


class SignupRequest(BaseModel):
    """Signup request payload"""
    username: str
    password: str
    email: str
    role: str  # admin, teacher, student
    student_id: Optional[str] = None  # Only for students
    name: str
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password length (bcrypt max is 72 bytes)"""
        if len(v) > 72:
            raise ValueError('Password must not exceed 72 characters (bcrypt limitation)')
        return v


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    role: str
    user_id: int
    username: str


# ==================== UTILITY FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash a password using SHA256 with salt"""
    # Use PBKDF2 style hashing with SHA256
    import hashlib
    import secrets
    
    # Generate a random salt
    salt = secrets.token_hex(32)
    
    # Hash password with salt using PBKDF2
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    
    # Return salt + hash combined
    return f"{salt}${pwd_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Split the stored hash into salt and hash
        salt, stored_hash = hashed_password.split('$')
        
        # Hash the provided password with the same salt
        pwd_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
        
        # Compare hashes
        return pwd_hash.hex() == stored_hash
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None or username is None or role is None:
            return None
        
        return TokenData(user_id=user_id, username=username, role=role)
    except JWTError:
        return None
