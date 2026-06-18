"""Tests for login endpoint."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
def registered_user(test_session: Session):
    """Create a registered user for testing login."""
    user = User(
        username="testuser",
        hashed_password=hash_password("password123")
    )
    test_session.add(user)
    test_session.flush()  # Flush to get the generated id without committing
    return user


def test_login_success(client: TestClient, registered_user: User):
    """Test successful login returns 200 with access_token and token_type."""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_case_insensitive_username(client: TestClient, registered_user: User):
    """Test login works with case variations of username."""
    # Try uppercase
    response = client.post(
        "/auth/login",
        json={"username": "TESTUSER", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    
    # Try mixed case
    response = client.post(
        "/auth/login",
        json={"username": "TestUser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_wrong_password(client: TestClient, registered_user: User):
    """Test login with wrong password returns 401 with specific error message."""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid username or password"


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent username returns 401 with same error message."""
    response = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "password123"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid username or password"


def test_login_same_error_for_wrong_password_and_nonexistent_user(
    client: TestClient, registered_user: User
):
    """Verify that wrong password and non-existent user return identical error messages."""
    # Wrong password
    response_wrong_password = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )
    
    # Non-existent user
    response_nonexistent = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "password123"}
    )
    
    # Both should return 401
    assert response_wrong_password.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_nonexistent.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Both should return identical error message
    assert response_wrong_password.json()["detail"] == response_nonexistent.json()["detail"]
    assert response_wrong_password.json()["detail"] == "Invalid username or password"


def test_login_invalid_credentials_validation(client: TestClient):
    """Test login with invalid credentials format (too short password)."""
    # Password too short (less than 8 chars) - should be caught by Pydantic validation
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "short"}
    )
    
    # Should return 422 for validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_generates_valid_jwt_token(client: TestClient, registered_user: User):
    """Test that login generates a valid JWT token that can be decoded."""
    from app.core.security import decode_access_token
    
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    
    # Decode the token to verify it contains correct payload
    payload = decode_access_token(token)
    assert "user_id" in payload
    assert "username" in payload
    assert payload["username"] == registered_user.username
    assert payload["user_id"] == str(registered_user.id)
