"""User Pydantic schemas for request validation and response serialization."""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Schema for user response (excludes password)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    username: str
    created_at: datetime


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str
