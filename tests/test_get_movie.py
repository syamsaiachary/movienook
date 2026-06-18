"""Test single movie retrieval endpoint."""

from uuid import uuid4


def test_get_movie_success(client):
    """Test retrieving own movie returns 200 with movie data."""
    # Register and login
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a movie
    create_response = client.post(
        "/movies",
        json={"title": "Test Movie", "genre": "Action", "rating": 8.5},
        headers=headers
    )
    assert create_response.status_code == 201
    movie_id = create_response.json()["id"]
    
    # Retrieve the movie
    response = client.get(f"/movies/{movie_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == movie_id
    assert data["title"] == "Test Movie"
    assert data["genre"] == "Action"
    assert data["rating"] == 8.5


def test_get_movie_not_found(client):
    """Test retrieving non-existent movie returns 404."""
    # Register and login
    client.post(
        "/auth/register",
        json={"username": "testuser2", "password": "password123"}
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser2", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to retrieve non-existent movie
    fake_id = str(uuid4())
    response = client.get(f"/movies/{fake_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}


def test_get_movie_unauthorized_access(client):
    """Test retrieving another user's movie returns 404."""
    # Register user A and create a movie
    client.post(
        "/auth/register",
        json={"username": "usera", "password": "password123"}
    )
    login_response_a = client.post(
        "/auth/login",
        json={"username": "usera", "password": "password123"}
    )
    token_a = login_response_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    create_response = client.post(
        "/movies",
        json={"title": "User A Movie"},
        headers=headers_a
    )
    movie_id = create_response.json()["id"]
    
    # Register user B
    client.post(
        "/auth/register",
        json={"username": "userb", "password": "password123"}
    )
    login_response_b = client.post(
        "/auth/login",
        json={"username": "userb", "password": "password123"}
    )
    token_b = login_response_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # User B tries to access User A's movie
    response = client.get(f"/movies/{movie_id}", headers=headers_b)
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie not found"}


def test_get_movie_without_auth(client):
    """Test retrieving movie without auth returns 401."""
    fake_id = str(uuid4())
    response = client.get(f"/movies/{fake_id}")
    assert response.status_code == 401
