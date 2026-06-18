"""Pytest configuration and fixtures for testing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.core.config import settings
from app.main import app
from app.dependencies import get_db


test_engine = create_engine(settings.TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database schema and clean up after all tests."""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Create fresh schema
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up after all tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_db):
    """Provide test database session with transaction rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_session(db_session):
    """Alias for db_session to support test files that expect test_session."""
    return db_session


@pytest.fixture
def client(db_session):
    """Provide test client with overridden database dependency."""
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
def auth_headers(client, db_session):
    """Create a test user and return authentication headers."""
    register_data = {
        "username": "testuser",
        "password": "password123"
    }
    client.post("/auth/register", json=register_data)
    
    login_response = client.post("/auth/login", json=register_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(client, db_session):
    """Create another test user and return authentication headers."""
    register_data = {
        "username": "otheruser",
        "password": "password456"
    }
    client.post("/auth/register", json=register_data)
    
    login_response = client.post("/auth/login", json=register_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
