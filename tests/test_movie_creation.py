"""Tests for movie creation endpoint."""

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


@pytest.fixture
def auth_token(client):
    """Register a user and return their JWT token."""
    # Register user
    client.post(
        "/auth/register",
        json={"username": "movieuser", "password": "password123"}
    )
    
    # Login to get token
    response = client.post(
        "/auth/login",
        json={"username": "movieuser", "password": "password123"}
    )
    
    return response.json()["access_token"]


def test_create_movie_success(client, auth_token):
    """Test creating a movie with valid data returns 201."""
    response = client.post(
        "/movies",
        json={
            "title": "The Matrix",
            "genre": "Sci-Fi",
            "rating": 9.5,
            "watched_date": "1999-03-31",
            "notes": "Mind-bending classic"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify all fields are present
    assert "id" in data
    assert "user_id" in data
    assert data["title"] == "The Matrix"
    assert data["genre"] == "Sci-Fi"
    assert data["rating"] == 9.5
    assert data["watched_date"] == "1999-03-31"
    assert data["notes"] == "Mind-bending classic"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_movie_minimal_fields(client, auth_token):
    """Test creating a movie with only required field (title) returns 201."""
    response = client.post(
        "/movies",
        json={"title": "Inception"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == "Inception"
    assert data["genre"] is None
    assert data["rating"] is None
    assert data["watched_date"] is None
    assert data["notes"] is None


def test_create_movie_empty_title(client, auth_token):
    """Test creating a movie with empty title returns 422."""
    response = client.post(
        "/movies",
        json={"title": ""},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 422
    assert response.json()["detail"] == "Title is required"


def test_create_movie_whitespace_title(client, auth_token):
    """Test creating a movie with whitespace-only title returns 422."""
    response = client.post(
        "/movies",
        json={"title": "   "},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 422
    assert response.json()["detail"] == "Title is required"


def test_create_movie_without_auth(client):
    """Test creating a movie without authentication returns 401."""
    response = client.post(
        "/movies",
        json={"title": "The Matrix"}
    )
    
    assert response.status_code == 401


def test_create_movie_sets_user_id_from_token(client, auth_token):
    """Test that user_id is set from JWT token, ignoring request body."""
    response = client.post(
        "/movies",
        json={
            "title": "Fight Club",
            "user_id": "00000000-0000-0000-0000-000000000000"  # Should be ignored
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # user_id should come from token, not from request body
    assert data["user_id"] != "00000000-0000-0000-0000-000000000000"


def test_create_movie_timestamps_equal(client, auth_token):
    """Test that created_at and updated_at are set to the same value on creation."""
    response = client.post(
        "/movies",
        json={"title": "Pulp Fiction"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Both timestamps should be present and equal
    assert data["created_at"] == data["updated_at"]
