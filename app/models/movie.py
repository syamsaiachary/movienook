from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from app.database import Base


class Movie(Base):
    """SQLAlchemy model for movies table."""
    
    __tablename__ = "movies"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to users
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Movie details
    title = Column(String(200), nullable=False)
    genre = Column(String(100), nullable=True)
    rating = Column(Float, nullable=True)
    watched_date = Column(Date, nullable=True)
    notes = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationship to User
    owner = relationship("User", back_populates="movies")
    
    # Table arguments - rating range constraint
    __table_args__ = (
        CheckConstraint('rating >= 1.0 AND rating <= 10.0', name='check_rating_range'),
    )
