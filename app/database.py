from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from app.core.config import settings

# Create sync engine with connection pooling configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using to prevent stale connection errors
    pool_size=2,
    max_overflow=3
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False  # Allow accessing attributes after commit without refetching
)

# Base class for SQLAlchemy models
Base = declarative_base()
