"""Security utilities for password hashing and JWT token operations."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Bcrypt hashed password string
        
    Requirements: 1.1, 12.2
    """
    # Convert password to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.
    
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to compare against
        
    Returns:
        True if password matches hash, False otherwise
        
    Requirements: 2.2, 12.4
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: UUID, username: str) -> str:
    """
    Generate a JWT access token with user_id, username, and expiration.
    
    The token payload contains:
    - user_id: UUID of the authenticated user
    - username: Username string
    - exp: Expiration timestamp (current time + TOKEN_EXPIRY_MINUTES)
    
    Args:
        user_id: UUID of the user
        username: Username string
        
    Returns:
        Encoded JWT token string
        
    Requirements: 2.3, 2.4, 2.7
    """
    # Calculate expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPIRY_MINUTES)
    
    # Create payload with user_id, username, and expiration
    payload = {
        "user_id": str(user_id),  # Convert UUID to string for JSON serialization
        "username": username,
        "exp": expire
    }
    
    # Encode and sign the JWT token
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.
    
    Validates the token signature and expiration. Raises exceptions
    from python-jose (ExpiredSignatureError, JWTError) without catching them,
    allowing calling code to handle authentication failures appropriately.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded token payload containing user_id and username
        
    Raises:
        ExpiredSignatureError: If the token has expired
        JWTError: If the token signature is invalid or token is malformed
        
    Requirements: 3.4, 3.5, 3.6
    """
    # Decode and verify JWT - let exceptions propagate uncaught
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    return payload
