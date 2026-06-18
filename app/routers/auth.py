"""Authentication endpoints for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with username and password.
    
    Validates username length (3-50) and password length (8+) via Pydantic schema.
    Checks username uniqueness with case-insensitive query.
    Hashes password with bcrypt and stores user record.
    
    Args:
        user_data: UserCreate schema with username and password
        db: Database session from dependency injection
        
    Returns:
        UserResponse with id, username, and created_at
        
    Raises:
        HTTPException(422): If username already exists (case-insensitive)
        
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 12.1
    """
    # Check username uniqueness with case-insensitive query
    existing_user = db.query(User).filter(
        func.lower(User.username) == func.lower(user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username already exists"
        )
    
    # Hash password with bcrypt
    hashed_password = hash_password(user_data.password)
    
    # Create new user record
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.flush()  # Flush to get the generated id and created_at
    
    # Return UserResponse (id, username, created_at)
    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token (JSON format).
    
    Accepts JSON body with username and password.
    For Swagger UI authentication, use POST /auth/token instead.
    
    Args:
        user_data: UserCreate schema with username and password
        db: Database session from dependency injection
        
    Returns:
        Token with access_token and token_type="bearer"
        
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 12.5
    """
    user = db.query(User).filter(
        func.lower(User.username) == func.lower(user_data.username)
    ).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(user_id=user.id, username=user.username)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2-compatible token endpoint for Swagger UI.
    
    This endpoint accepts form data (not JSON) to work with Swagger's Authorize button.
    Use this endpoint when clicking the lock icon in Swagger UI.
    
    Args:
        form_data: OAuth2PasswordRequestForm with username and password
        db: Database session
        
    Returns:
        Token with access_token and token_type="bearer"
    """
    user = db.query(User).filter(
        func.lower(User.username) == func.lower(form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user_id=user.id, username=user.username)
    return Token(access_token=access_token, token_type="bearer")
