"""Tests for FastAPI application initialization."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_cors_middleware_configured(test_client):
    """Verify CORS middleware is configured correctly."""
    # Check middleware is present
    cors_middleware = None
    for middleware in app.user_middleware:
        if "CORSMiddleware" in str(middleware.cls):
            cors_middleware = middleware
            break
    
    assert cors_middleware is not None, "CORSMiddleware not found"
    
    # Verify CORS configuration
    kwargs = cors_middleware.kwargs
    assert "allow_origins" in kwargs
    assert isinstance(kwargs["allow_origins"], list)
    assert len(kwargs["allow_origins"]) == 1  # No wildcard, specific origin
    assert kwargs["allow_credentials"] is True
    assert set(kwargs["allow_methods"]) == {"GET", "POST", "PATCH", "DELETE"}
    assert set(kwargs["allow_headers"]) == {"Authorization", "Content-Type"}


def test_global_exception_handler():
    """Verify global exception handler is registered."""
    assert Exception in app.exception_handlers
    assert callable(app.exception_handlers[Exception])


def test_global_exception_handler_returns_500():
    """Verify global exception handler returns 500 with correct message."""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import asyncio
    
    # Test the exception handler directly
    exception_handler = app.exception_handlers[Exception]
    
    # Create a mock request
    mock_request = type('Request', (), {})()
    test_exception = ValueError("Test exception")
    
    # Call the handler
    response = asyncio.run(exception_handler(mock_request, test_exception))
    
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body.decode() == '{"detail":"Internal server error"}'
