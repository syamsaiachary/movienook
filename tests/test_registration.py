"""Tests for user registration endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.dependencies import get_db
from app.core.config import settings


# Create test engine and session
test_engine = create_engine(settings.TEST_DATABASE_URL.replace("+asyncpg", ""))
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="module")
def setup_test_db():
    """Create test database schema."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_db):
    """Provide test database session."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """Provide test client with overridden database dependency."""
    from app.main import app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


def test_register_success(client):
    """Test successful user registration returns 201 with user data."""
    response = client.post(
        "/auth/register",
        json={"username": "testuser123", "password": "password123"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response contains required fields
    assert "id" in data
    assert data["username"] == "testuser123"
    assert "created_at" in data
    
    # Verify password is not returned
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username_case_insensitive(client):
    """Test registering duplicate username (case-insensitive) returns 422."""
    # Register first user
    client.post(
        "/auth/register",
        json={"username": "UniqueUser", "password": "password123"}
    )
    
    # Attempt to register with case variation
    response = client.post(
        "/auth/register",
        json={"username": "uniqueuser", "password": "different456"}
    )
    
    assert response.status_code == 422
    assert response.json()["detail"] == "Username already exists"


def test_register_username_too_short(client):
    """Test username shorter than 3 characters returns validation error."""
    response = client.post(
        "/auth/register",
        json={"username": "ab", "password": "password123"}
    )
    
    assert response.status_code == 422


def test_register_password_too_short(client):
    """Test password shorter than 8 characters returns validation error."""
    response = client.post(
        "/auth/register",
        json={"username": "validuser", "password": "short"}
    )
    
    assert response.status_code == 422
