# Implementation Plan: Movie Tracking API

## Overview

This implementation plan breaks down the movie tracking API into discrete coding tasks. The API is a FastAPI-based REST service with JWT authentication, PostgreSQL database, and complete CRUD operations for user-owned movie entries. All tasks build incrementally toward a working system with strict user data isolation.

## Tasks

- [x] 1. Set up project structure and configuration
  - Create directory structure following project layout (app/, alembic/, tests/)
  - Create requirements.txt with all dependencies (FastAPI, SQLAlchemy, psycopg2-binary, Alembic, Pydantic, python-jose, passlib[bcrypt], pytest, httpx)
  - Create .env.example with JWT_SECRET, DATABASE_URL, TEST_DATABASE_URL, TOKEN_EXPIRY_MINUTES, FRONTEND_URL
  - Implement Settings class in app/core/config.py using pydantic-settings with field validator for JWT_SECRET length (min 32 chars) — kept as explicit security validation, distinct from the over-engineered startup validation removed elsewhere in the design; include FRONTEND_URL field
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 2. Implement database connection and base models
  - [x] 2.1 Create database engine and session management
    - Implement app/database.py with create_engine, sessionmaker, and Base
    - Configure engine with pool_pre_ping=True, expire_on_commit=False
    - Use postgresql:// or postgresql+psycopg2:// URL scheme from settings
    - _Requirements: 9.2_
  
  - [x] 2.2 Create User SQLAlchemy model
    - Implement app/models/user.py with User class
    - Define columns: id (UUID PK), username (VARCHAR 50), hashed_password (VARCHAR 255), created_at (TIMESTAMP TZ)
    - Add case-insensitive unique index on username using func.lower()
    - Add relationship to movies with cascade delete-orphan
    - _Requirements: 9.1, 9.5, 9.6_
  
  - [x] 2.3 Create Movie SQLAlchemy model
    - Implement app/models/movie.py with Movie class
    - Define columns: id (UUID PK), user_id (UUID FK), title, genre, rating, watched_date, notes, created_at, updated_at
    - Add CheckConstraint for rating range (1.0-10.0)
    - Add ForeignKey with ondelete="CASCADE"
    - Add relationship to User
    - Set both created_at and updated_at defaults to datetime.now(timezone.utc)
    - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [x] 3. Set up Alembic migrations
  - [x] 3.1 Initialize Alembic and configure
    - Run alembic init alembic
    - Configure alembic.ini with sqlalchemy.url from settings
    - Update env.py to use sync engine and import Base metadata
    - _Requirements: 10.1, 10.2_
  
  - [x] 3.2 Generate initial migration for users and movies tables
    - Generate migration with alembic revision --autogenerate
    - Review migration file to ensure correct schema (UUID types, constraints, indexes)
    - _Requirements: 10.3_

- [x] 4. Implement security utilities
  - [x] 4.1 Create password hashing functions
    - Implement hash_password() and verify_password() in app/core/security.py
    - Use passlib.context.CryptContext with bcrypt scheme
    - Use default bcrypt work factor (do not hardcode rounds parameter)
    - _Requirements: 1.1, 2.2, 12.2, 12.4_
  
  - [x] 4.2 Create JWT token functions
    - Implement create_access_token() that generates JWT with user_id, username, and exp in payload
    - Implement decode_access_token() that validates signature and expiration, letting python-jose's ExpiredSignatureError and JWTError propagate uncaught
    - Use python-jose for JWT operations with settings.JWT_SECRET
    - _Requirements: 2.3, 2.4, 2.7, 3.4, 3.5, 3.6_

- [x] 5. Create Pydantic schemas
  - [x] 5.1 Implement user schemas
    - Create app/schemas/user.py with UserCreate, UserResponse, Token classes
    - UserCreate: username (min 3, max 50), password (min 8)
    - UserResponse: id, username, created_at with from_attributes=True
    - Token: access_token, token_type
    - _Requirements: 1.5, 1.6_
  
  - [x] 5.2 Implement movie schemas
    - Create app/schemas/movie.py with MovieCreate, MovieUpdate, MovieResponse classes
    - MovieCreate: title (max 200), genre (max 100), rating (1.0-10.0), watched_date, notes (max 1000)
    - MovieUpdate: all fields optional with same constraints
    - MovieResponse: all fields including timestamps with from_attributes=True
    - _Requirements: 4.2, 4.4, 4.5, 4.6, 4.7_

- [x] 6. Implement database and authentication dependencies
  - [x] 6.1 Create database session dependency
    - Implement get_db() in app/dependencies.py as a generator function (def, yield)
    - Yield Session with automatic commit on success, rollback on exception
    - _Requirements: 9.2_
  
  - [x] 6.2 Create authentication dependency
    - Implement OAuth2PasswordBearer scheme for token extraction
    - Implement get_current_user() that extracts token, decodes JWT via decode_access_token(), queries user by id
    - Catch ExpiredSignatureError and raise HTTPException(401, "Token has expired")
    - Catch JWTError and raise HTTPException(401, "Invalid authentication credentials")
    - Raise HTTPException(401, "Not authenticated") for missing header or invalid format
    - Raise HTTPException(401, "Invalid authentication credentials") for user not found
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 7. Implement authentication endpoints
  - [x] 7.1 Create registration endpoint
    - Implement POST /auth/register in app/routers/auth.py
    - Validate username length (3-50) and password length (8+) via Pydantic
    - Check username uniqueness with case-insensitive query using func.lower()
    - Raise HTTPException(422, "Username already exists") if duplicate
    - Hash password with bcrypt and store user record
    - Return 201 with UserResponse (id, username, created_at)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 12.1_
  
  - [x] 7.2 Create login endpoint
    - Implement POST /auth/login in app/routers/auth.py
    - Accept JSON body with username and password (not OAuth2 form)
    - Query user by username with case-insensitive comparison
    - Verify password with verify_password()
    - Return same error message for non-existent user and wrong password: HTTPException(401, "Invalid username or password")
    - Generate JWT token with user_id and username payload
    - Return 200 with {"access_token": token, "token_type": "bearer"}
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 12.5_

- [x] 8. Implement movie CRUD endpoints
  - [x] 8.1 Create movie creation endpoint
    - Implement POST /movies in app/routers/movies.py
    - Require authentication via current_user dependency
    - Check if title is empty or whitespace, raise HTTPException(422, "Title is required")
    - Validate all field lengths and rating range via Pydantic and custom checks
    - Set user_id from JWT payload (current_user.id), ignore any user_id in request body
    - Set both created_at and updated_at to same value at creation
    - Return 201 with MovieResponse including all fields
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 13.2, 13.4, 13.5_
  
  - [x] 8.2 Create movie listing endpoint with filtering and sorting
    - Implement GET /movies in app/routers/movies.py
    - Require authentication via current_user dependency
    - Filter by user_id from JWT payload automatically
    - Add optional genre query parameter with case-insensitive ILIKE filtering
    - Add optional sort_by parameter (title, watched_date) with validation
    - Add optional order parameter (asc, desc) with validation, default to asc
    - Apply sorting: title lexicographically, watched_date chronologically with nulls last
    - Raise HTTPException(422) for invalid sort_by or order values
    - Return 200 with JSON array (empty array if no movies)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 13.1_
  
  - [x] 8.3 Create single movie retrieval endpoint
    - Implement GET /movies/{movie_id} in app/routers/movies.py
    - Use UUID path parameter type hint for automatic validation
    - Require authentication via current_user dependency
    - Query movie by id AND user_id match
    - Return 404 "Movie not found" for non-existent movie OR unauthorized access (same message)
    - Return 200 with MovieResponse if authorized
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 13.3, 13.6_
  
  - [x] 8.4 Create movie update endpoint
    - Implement PATCH /movies/{movie_id} in app/routers/movies.py
    - Use UUID path parameter type hint for automatic validation
    - Require authentication via current_user dependency
    - Query movie by id AND user_id match
    - Return 404 "Movie not found" for non-existent or unauthorized access
    - Check if any fields provided, raise HTTPException(422, "No fields to update") if none
    - Validate provided fields (title, genre, rating, watched_date, notes) with same constraints as creation
    - Update only provided fields using exclude_unset=True
    - Set updated_at to current UTC time
    - Return 200 with updated MovieResponse
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 13.3, 13.7_
  
  - [x] 8.5 Create movie deletion endpoint
    - Implement DELETE /movies/{movie_id} in app/routers/movies.py
    - Use UUID path parameter type hint for automatic validation
    - Require authentication via current_user dependency
    - Query movie by id AND user_id match
    - Return 404 "Movie not found" for non-existent or unauthorized access
    - Delete the movie record from database
    - Return 204 with no response body
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 13.3, 13.8_

- [x] 9. Implement FastAPI application initialization
  - Create app/main.py with FastAPI app instance
  - Register auth and movies routers
  - Add global exception handler for unhandled exceptions (return 500 "Internal server error")
  - Configure CORSMiddleware with allow_origins read from FRONTEND_URL setting (no wildcard origins), allow_credentials=True, allow_methods restricted to GET/POST/PATCH/DELETE, allow_headers=['Authorization', 'Content-Type']
  - _Requirements: 4.9_

- [x] 10. Checkpoint - Ensure all tests pass
  - Run alembic upgrade head to apply migrations to test database
  - Run pytest to execute all tests
  - Verify no import errors or schema issues
  - Ask the user if questions arise

- [x] 11. Implement pytest test suite
  - [x] 11.1 Create test fixtures and configuration
    - Implement conftest.py with test_engine, test_session, and client fixtures
    - Configure test database with TEST_DATABASE_URL from settings
    - Create schema with Base.metadata.create_all in session scope
    - Override get_db dependency with test_session
    - Use TestClient (not AsyncClient) for testing sync endpoints; test functions are plain def, not async def
    - _Requirements: 14.13_
  
  - [x] 11.2 Write authentication tests*
    - Test successful registration returns 201 with id, username, created_at
    - Test successful login returns 200 with access_token and token_type
    - Parametrised test for login failures (wrong password, non-existent user) returns 401
    - _Requirements: 14.2, 14.3, 14.4_
  
  - [x] 11.3 Write movie CRUD tests*
    - Test creating movie with valid JWT returns 201 with all fields
    - Test creating movie without title returns 422
    - Test listing movies returns 200 with only authenticated user's movies
    - Test listing movies returns empty array when user has no movies
    - Test deleting movie with valid JWT returns 204
    - _Requirements: 14.5, 14.6, 14.7, 14.8, 14.12_
  
  - [x] 11.4 Verify user isolation (required)
    - Test fetching another user's movie returns 404
    - Test updating another user's movie returns 404
    - _Requirements: 14.9, 14.10_
  
  - [x] 11.5 Write authentication protection tests*
    - Test protected endpoint without JWT returns 401 "Not authenticated"
    - _Requirements: 14.11_

- [x] 12. Final checkpoint - Verify complete system
  - Run full test suite with pytest -v
  - Verify all endpoints work correctly
  - Check error handling for all edge cases
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP, except user-isolation tests (11.4) which are required
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout implementation
- All movie operations enforce user data isolation via JWT payload user_id
- Password hashing uses bcrypt with passlib default work factor
- All validation errors return consistent {"detail": "message"} format via HTTPException(422)
- Database operations use sync SQLAlchemy with psycopg2 driver
- FastAPI path parameter UUID type hints handle invalid UUID format automatically

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1"]
    },
    {
      "id": 1,
      "tasks": ["2.1", "3.1"]
    },
    {
      "id": 2,
      "tasks": ["2.2", "2.3"]
    },
    {
      "id": 3,
      "tasks": ["3.2", "4.1", "5.1"]
    },
    {
      "id": 4,
      "tasks": ["4.2", "5.2", "6.1"]
    },
    {
      "id": 5,
      "tasks": ["6.2"]
    },
    {
      "id": 6,
      "tasks": ["7.1", "7.2"]
    },
    {
      "id": 7,
      "tasks": ["8.1", "8.2", "8.3", "8.4", "8.5"]
    },
    {
      "id": 8,
      "tasks": ["9"]
    },
    {
      "id": 9,
      "tasks": ["11.1"]
    },
    {
      "id": 10,
      "tasks": ["11.2", "11.3", "11.4", "11.5"]
    }
  ]
}
```
