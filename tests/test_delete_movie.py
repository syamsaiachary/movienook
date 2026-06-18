"""Tests for movie deletion endpoint."""

from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from app.models.movie import Movie
from app.core.security import decode_access_token


def test_delete_movie_success(client: TestClient, db_session, auth_headers):
    """Test successful movie deletion."""
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=user_id,
        title="Test Movie",
        genre="Action",
        rating=8.5
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.delete(
        f"/movies/{movie_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ""
    
    deleted_movie = db_session.query(Movie).filter(Movie.id == movie_id).first()
    assert deleted_movie is None


def test_delete_movie_not_found(client: TestClient, auth_headers):
    """Test deleting non-existent movie returns 404."""
    non_existent_id = uuid4()
    
    response = client.delete(
        f"/movies/{non_existent_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Movie not found"


def test_delete_movie_unauthorized(client: TestClient, db_session, auth_headers, other_user_headers):
    """Test deleting another user's movie returns 404."""
    token = other_user_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    other_user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=other_user_id,
        title="Other User's Movie",
        genre="Drama",
        rating=7.0
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.delete(
        f"/movies/{movie_id}",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Movie not found"
    
    movie_still_exists = db_session.query(Movie).filter(Movie.id == movie_id).first()
    assert movie_still_exists is not None


def test_delete_movie_without_auth(client: TestClient, db_session, auth_headers):
    """Test deleting movie without authentication returns 401."""
    token = auth_headers["Authorization"].split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload["user_id"]
    
    movie = Movie(
        id=uuid4(),
        user_id=user_id,
        title="Test Movie",
        genre="Action",
        rating=8.5
    )
    db_session.add(movie)
    db_session.flush()
    movie_id = movie.id
    
    response = client.delete(f"/movies/{movie_id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
