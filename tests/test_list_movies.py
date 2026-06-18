"""Tests for GET /movies endpoint with filtering and sorting."""

import pytest
from datetime import date


def test_list_movies_empty(client, auth_headers):
    """Test listing movies returns empty array when user has no movies."""
    response = client.get("/movies", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_movies_returns_user_movies_only(client, auth_headers, other_user_headers):
    """Test listing movies returns only authenticated user's movies."""
    movie1_data = {"title": "Inception", "genre": "Sci-Fi", "rating": 9.5}
    response1 = client.post("/movies", json=movie1_data, headers=auth_headers)
    assert response1.status_code == 201
    
    movie2_data = {"title": "The Matrix", "genre": "Sci-Fi", "rating": 9.0}
    response2 = client.post("/movies", json=movie2_data, headers=other_user_headers)
    assert response2.status_code == 201
    
    response = client.get("/movies", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Inception"


def test_list_movies_filter_by_genre(client, auth_headers):
    """Test filtering movies by genre (case-insensitive)."""
    client.post("/movies", json={"title": "Inception", "genre": "Sci-Fi"}, headers=auth_headers)
    client.post("/movies", json={"title": "The Godfather", "genre": "Drama"}, headers=auth_headers)
    client.post("/movies", json={"title": "Interstellar", "genre": "sci-fi"}, headers=auth_headers)
    
    response = client.get("/movies?genre=sci-fi", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [m["title"] for m in data]
    assert "Inception" in titles
    assert "Interstellar" in titles


def test_list_movies_sort_by_title(client, auth_headers):
    """Test sorting movies by title."""
    client.post("/movies", json={"title": "Zoolander"}, headers=auth_headers)
    client.post("/movies", json={"title": "Inception"}, headers=auth_headers)
    client.post("/movies", json={"title": "Avatar"}, headers=auth_headers)
    
    response = client.get("/movies?sort_by=title", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    titles = [m["title"] for m in data]
    assert titles == ["Avatar", "Inception", "Zoolander"]
    
    response = client.get("/movies?sort_by=title&order=desc", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    titles = [m["title"] for m in data]
    assert titles == ["Zoolander", "Inception", "Avatar"]


def test_list_movies_sort_by_watched_date(client, auth_headers):
    """Test sorting movies by watched_date with nulls last."""
    client.post("/movies", json={"title": "Old Movie", "watched_date": "2020-01-01"}, headers=auth_headers)
    client.post("/movies", json={"title": "Not Watched"}, headers=auth_headers)
    client.post("/movies", json={"title": "Recent Movie", "watched_date": "2023-06-15"}, headers=auth_headers)
    
    response = client.get("/movies?sort_by=watched_date&order=asc", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    titles = [m["title"] for m in data]
    assert titles == ["Old Movie", "Recent Movie", "Not Watched"]
    
    response = client.get("/movies?sort_by=watched_date&order=desc", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    titles = [m["title"] for m in data]
    assert titles == ["Recent Movie", "Old Movie", "Not Watched"]


def test_list_movies_invalid_sort_by(client, auth_headers):
    """Test invalid sort_by value returns 422."""
    response = client.get("/movies?sort_by=rating", headers=auth_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid sort_by value. Must be 'title' or 'watched_date'"}


def test_list_movies_invalid_order(client, auth_headers):
    """Test invalid order value returns 422."""
    response = client.get("/movies?sort_by=title&order=invalid", headers=auth_headers)
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid order value. Must be 'asc' or 'desc'"}


def test_list_movies_without_auth(client):
    """Test listing movies without authentication returns 401."""
    response = client.get("/movies")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
