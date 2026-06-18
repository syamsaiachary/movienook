"""Movie management endpoints."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.movie import Movie
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse


router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie_data: MovieCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Create a new movie for the authenticated user.
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 13.2, 13.4, 13.5
    """
    if not movie_data.title or not movie_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title is required"
        )
    
    now = datetime.now(timezone.utc)
    movie = Movie(
        user_id=current_user.id,
        title=movie_data.title,
        genre=movie_data.genre,
        rating=movie_data.rating,
        watched_date=movie_data.watched_date,
        notes=movie_data.notes,
        created_at=now,
        updated_at=now
    )
    
    db.add(movie)
    db.flush()
    db.refresh(movie)
    
    return movie


@router.get("", response_model=List[MovieResponse], status_code=status.HTTP_200_OK)
def list_movies(
    genre: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    order: Optional[str] = Query("asc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[MovieResponse]:
    """
    List movies for authenticated user with optional filtering and sorting.
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 13.1
    """
    if sort_by is not None and sort_by not in ["title", "watched_date"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid sort_by value. Must be 'title' or 'watched_date'"
        )
    
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid order value. Must be 'asc' or 'desc'"
        )
    
    query = db.query(Movie).filter(Movie.user_id == current_user.id)
    
    if genre is not None:
        query = query.filter(Movie.genre.ilike(genre))
    
    if sort_by is not None:
        sort_column = getattr(Movie, sort_by)
        if order == "desc":
            if sort_by == "watched_date":
                query = query.order_by(desc(sort_column).nullslast())
            else:
                query = query.order_by(desc(sort_column))
        else:
            if sort_by == "watched_date":
                query = query.order_by(asc(sort_column).nullslast())
            else:
                query = query.order_by(asc(sort_column))
    
    return query.all()


@router.get("/{movie_id}", response_model=MovieResponse, status_code=status.HTTP_200_OK)
def get_movie(
    movie_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 13.3, 13.6
    """
    movie = db.query(Movie).filter(
        Movie.id == movie_id,
        Movie.user_id == current_user.id
    ).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return movie


@router.patch("/{movie_id}", response_model=MovieResponse, status_code=status.HTTP_200_OK)
def update_movie(
    movie_id: UUID,
    movie_data: MovieUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MovieResponse:
    """
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 13.3, 13.7
    """
    movie = db.query(Movie).filter(
        Movie.id == movie_id,
        Movie.user_id == current_user.id
    ).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    update_data = movie_data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields to update"
        )
    
    if "title" in update_data and (not update_data["title"] or not update_data["title"].strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title is required"
        )
    
    for field, value in update_data.items():
        setattr(movie, field, value)
    
    movie.updated_at = datetime.now(timezone.utc)
    
    db.flush()
    db.refresh(movie)
    
    return movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 13.3, 13.8
    """
    movie = db.query(Movie).filter(
        Movie.id == movie_id,
        Movie.user_id == current_user.id
    ).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    db.delete(movie)
    db.flush()
