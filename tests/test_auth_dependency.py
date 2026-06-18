"""Tests for authentication dependency (get_current_user)."""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from fastapi import HTTPException
from jose import jwt

from app.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User


def test_get_current_user_missing_token(test_session):
    """Test that missing token raises 401 Not authenticated."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="", db=test_session)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


def test_get_current_user_expired_token(test_session):
    """Test that expired token raises 401 Token has expired."""
    # Create a user
    user = User(
        id=uuid4(),
        username="testuser",
        hashed_password="hashedpassword123",
        created_at=datetime.now(timezone.utc)
    )
    test_session.add(user)
    test_session.commit()
    
    # Create expired token
    expire = datetime.now(timezone.utc) - timedelta(minutes=5)  # 5 minutes ago
    payload = {
        "user_id": str(user.id),
        "username": user.username,
        "exp": expire
    }
    expired_token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=expired_token, db=test_session)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


def test_get_current_user_invalid_signature(test_session):
    """Test that token with invalid signature raises 401 Invalid authentication credentials."""
    # Create token with wrong secret
    payload = {
        "user_id": str(uuid4()),
        "username": "testuser",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    invalid_token = jwt.encode(payload, "wrong_secret_key", algorithm="HS256")
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=invalid_token, db=test_session)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_get_current_user_malformed_token(test_session):
    """Test that malformed token raises 401 Invalid authentication credentials."""
    malformed_token = "not.a.valid.jwt.token"
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=malformed_token, db=test_session)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_get_current_user_user_not_found(test_session):
    """Test that valid token with non-existent user raises 401 Invalid authentication credentials."""
    # Create token for non-existent user
    non_existent_user_id = uuid4()
    payload = {
        "user_id": str(non_existent_user_id),
        "username": "nonexistent",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=test_session)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_get_current_user_valid_token(test_session):
    """Test that valid token returns the correct user."""
    # Create a user
    user = User(
        id=uuid4(),
        username="validuser",
        hashed_password="hashedpassword123",
        created_at=datetime.now(timezone.utc)
    )
    test_session.add(user)
    test_session.commit()
    
    # Create valid token
    payload = {
        "user_id": str(user.id),
        "username": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    valid_token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    # Call get_current_user
    authenticated_user = get_current_user(token=valid_token, db=test_session)
    
    assert authenticated_user.id == user.id
    assert authenticated_user.username == user.username
