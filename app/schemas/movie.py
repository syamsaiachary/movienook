"""Movie Pydantic schemas for request validation and response serialization."""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional


class MovieCreate(BaseModel):
    """Schema for movie creation request.
    
    Title validation for empty/whitespace is handled in the route handler
    to ensure consistent {"detail": "..."} format for all 422 errors.
    """
    title: str = Field(..., max_length=200)
    genre: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    watched_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class MovieUpdate(BaseModel):
    """Schema for movie update request.
    
    All fields are optional to support partial updates.
    Same validation constraints as MovieCreate.
    """
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    
    title: Optional[str] = Field(None, max_length=200)
    genre: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    watched_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class MovieResponse(BaseModel):
    """Schema for movie response including all fields and timestamps."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    title: str
    genre: Optional[str]
    rating: Optional[float]
    watched_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
