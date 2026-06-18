"""Tests for movie update endpoint."""

from uuid import uuid4
from datetime import date, datetime, timezone

from fastapi import status
from fastapi.testclient import TestClient

from app.models.movie import Movie
from app.core.security import decode_access_token


def test_update_movie_success(client: TestClient, db_session, auth_headers):
    """Test successful movie update returns 200 with updated data."""
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=user_id,
        title="Original Title",
        genre="Action",
        rating=7.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.patch(
        f"/movies/{movie_id}",
        json={"title": "Updated Title", "rating": 9.0},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["rating"] == 9.0
    assert data["genre"] == "Action"


def test_update_another_users_movie_returns_404(client: TestClient, db_session, auth_headers, other_user_headers):
    """Test updating another user's movie returns 404."""
    token = other_user_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    other_user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=other_user_id,
        title="Other User's Movie",
        genre="Drama",
        rating=8.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.patch(
        f"/movies/{movie_id}",
        json={"title": "Hacked Title"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Movie not found"
    
    db_session.refresh(movie)
    assert movie.title == "Other User's Movie"


def test_update_nonexistent_movie_returns_404(client: TestClient, auth_headers):
    """Test updating non-existent movie returns 404."""
    non_existent_id = uuid4()
    
    response = client.patch(
        f"/movies/{non_existent_id}",
        json={"title": "New Title"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Movie not found"


def test_update_movie_without_auth_returns_401(client: TestClient, db_session, auth_headers):
    """Test updating movie without authentication returns 401."""
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=user_id,
        title="Test Movie",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.patch(
        f"/movies/{movie_id}",
        json={"title": "Updated Title"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_movie_partial_fields(client: TestClient, db_session, auth_headers):
    """Test partial updates only modify specified fields."""
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=user_id,
        title="Original Title",
        genre="Action",
        rating=7.5,
        watched_date=date(2024, 1, 15),
        notes="Original notes",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.patch(
        f"/movies/{movie_id}",
        json={"rating": 9.0},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["rating"] == 9.0
    assert data["title"] == "Original Title"
    assert data["genre"] == "Action"
    assert data["watched_date"] == "2024-01-15"
    assert data["notes"] == "Original notes"


def test_update_movie_changes_updated_at_timestamp(client: TestClient, db_session, auth_headers):
    """Test that updated_at timestamp changes on update."""
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload["user_id"]
    
    original_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    movie = Movie(
        id=uuid4(),
        user_id=user_id,
        title="Test Movie",
        created_at=original_time,
        updated_at=original_time
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.patch(
        f"/movies/{movie_id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
    assert updated_at > original_time
