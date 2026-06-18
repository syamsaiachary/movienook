from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timezone

from app.database import Base


class User(Base):
    """SQLAlchemy model for users table."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User credentials
    username = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationship to movies with cascade delete-orphan
    movies = relationship("Movie", back_populates="owner", cascade="all, delete-orphan")
    
    # Table arguments - case-insensitive unique index on username
    __table_args__ = (
        Index('ix_users_username_lower', func.lower(username), unique=True),
    )
