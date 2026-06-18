"""
Tests for configuration validation.

These tests verify that the Settings class properly validates
environment variables at startup.
"""
import pytest
from pydantic import ValidationError


def test_jwt_secret_minimum_length():
    """Test that JWT_SECRET must be at least 32 characters."""
    from app.core.config import Settings
    
    # This should raise a ValidationError because JWT_SECRET is too short
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            JWT_SECRET="short",  # Only 5 characters
            DATABASE_URL="postgresql+asyncpg://localhost/test",
            TEST_DATABASE_URL="postgresql+asyncpg://localhost/test",
            FRONTEND_URL="http://localhost:3000"
        )
    
    # Verify the error message mentions the length requirement
    assert "at least 32 characters" in str(exc_info.value)


def test_jwt_secret_valid_length():
    """Test that JWT_SECRET with 32+ characters is accepted."""
    from app.core.config import Settings
    
    # This should succeed with a 32+ character secret
    settings = Settings(
        JWT_SECRET="a" * 32,  # Exactly 32 characters
        DATABASE_URL="postgresql+asyncpg://localhost/test",
        TEST_DATABASE_URL="postgresql+asyncpg://localhost/test_db",
        FRONTEND_URL="http://localhost:3000"
    )
    
    assert len(settings.JWT_SECRET) >= 32
    assert settings.TOKEN_EXPIRY_MINUTES == 1440  # Default value
