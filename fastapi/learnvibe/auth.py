
#new one
from fastapi import Depends, HTTPException,status
from fastapi import security
from fastapi.security import HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import random
import string
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration - Hardcoded secret key
SECRET_KEY = "xK8vQ2nP_7mR4jL9sH3tA6fB1wE5yU0cG2dN8pM4qV6zT3yH9mL2pW5sA8fD1gJ4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    """Verify a plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_reset_code(length: int = 6) -> str:
    """Generate a random numeric reset code"""
    return ''.join(random.choices(string.digits, k=length))

def validate_reset_code(code: str) -> bool:
    """Validate reset code format"""
    return len(code) == 6 and code.isdigit()

# Add this to your existing auth.py file, after the existing functions

# Token blacklist (in production, use Redis or database)
token_blacklist = set()

def verify_token_not_blacklisted(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the JWT token and check if it's blacklisted
    """
    try:
        token = credentials.credentials
        
        # Check if token is blacklisted
        if token in token_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated"
            )
        
        # Verify JWT token signature and expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )