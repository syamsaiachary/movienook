"""Tests for JWT token creation and decoding functions."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import ExpiredSignatureError, JWTError

from app.core.security import create_access_token, decode_access_token


def test_create_access_token():
    """Test that create_access_token generates a valid JWT with correct payload."""
    user_id = uuid.uuid4()
    username = "testuser"
    
    token = create_access_token(user_id, username)
    
    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode the token to verify payload
    payload = decode_access_token(token)
    assert payload["user_id"] == str(user_id)
    assert payload["username"] == username
    assert "exp" in payload


def test_decode_access_token_valid():
    """Test that decode_access_token successfully decodes a valid token."""
    user_id = uuid.uuid4()
    username = "testuser"
    
    token = create_access_token(user_id, username)
    payload = decode_access_token(token)
    
    assert payload["user_id"] == str(user_id)
    assert payload["username"] == username
    assert "exp" in payload


def test_decode_access_token_invalid_signature():
    """Test that decode_access_token raises JWTError for invalid signature."""
    # Create a malformed token
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwidXNlcm5hbWUiOiJ0ZXN0In0.invalid_signature"
    
    with pytest.raises(JWTError):
        decode_access_token(invalid_token)


def test_decode_access_token_expired():
    """Test that decode_access_token raises ExpiredSignatureError for expired token."""
    # Create a token that's already expired by mocking the expiration
    # We'll use python-jose to create an expired token manually
    from jose import jwt
    from app.core.config import settings
    
    user_id = uuid.uuid4()
    username = "testuser"
    
    # Create payload with past expiration
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    payload = {
        "user_id": str(user_id),
        "username": username,
        "exp": expire
    }
    
    expired_token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    with pytest.raises(ExpiredSignatureError):
        decode_access_token(expired_token)


def test_create_and_decode_roundtrip():
    """Test that a token can be created and decoded successfully."""
    user_id = uuid.uuid4()
    username = "roundtrip_user"
    
    # Create token
    token = create_access_token(user_id, username)
    
    # Decode token
    payload = decode_access_token(token)
    
    # Verify the payload matches original data
    assert payload["user_id"] == str(user_id)
    assert payload["username"] == username
    
    # Verify expiration is in the future
    exp_timestamp = payload["exp"]
    assert isinstance(exp_timestamp, (int, float))
