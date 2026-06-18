# Requirements Document

## Introduction

This document defines the functional requirements for a FastAPI-based REST API backend that enables individual users to track their personal movie watch lists. The system provides user authentication via JWT tokens and complete CRUD operations for movie entries. Each user's data is strictly isolated with no cross-user access or sharing capabilities.

## Glossary

- **System**: The movie tracking REST API backend
- **User**: A registered individual with authentication credentials who owns a private movie collection
- **Movie_Entry**: A record representing a movie with metadata (title, genre, rating, watched date, notes) owned by a specific User
- **JWT_Token**: JSON Web Token containing user_id and username used for authenticating API requests
- **Auth_Service**: The authentication subsystem responsible for user registration and login
- **Movie_Service**: The movie management subsystem responsible for CRUD operations on Movie_Entry records
- **Database**: PostgreSQL database storing users and movies tables with foreign key relationships

## Requirements

### Requirement 1: User Registration

**User Story:** As a new user, I want to register with a username and password, so that I can create an account to track my movies.

#### Acceptance Criteria

1. WHEN a registration request is received with username and password fields, IF the username is between 3 and 50 characters AND password is at least 8 characters, THEN THE Auth_Service SHALL hash the password using bcrypt
2. WHEN the password is hashed, THE Auth_Service SHALL store the user record with username and hashed_password in the Database
3. WHEN the user record is stored successfully, THE Auth_Service SHALL return HTTP status 201 with a JSON response body containing: id (UUID), username (string), and created_at (ISO 8601 timestamp)
4. IF a username already exists in the Database (case-insensitive comparison), THEN THE Auth_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Username already exists"}
5. IF the username is shorter than 3 characters or longer than 50 characters, THEN THE Auth_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Username must be between 3 and 50 characters"}
6. IF the password is shorter than 8 characters, THEN THE Auth_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Password must be at least 8 characters"}

> **Implementation note:** Validation errors in criteria 4–6 are raised as HTTPException with status 422, not as Pydantic ValidationError. This ensures all 422 responses return a consistent `{"detail": "<message>"}` shape rather than FastAPI's default list-based Pydantic error format.

### Requirement 2: User Login and JWT Token Generation

**User Story:** As a registered user, I want to log in with my credentials, so that I can receive a JWT token to access my movie list.

#### Acceptance Criteria

1. WHEN a login request is received with a JSON body containing username (string) and password (string) fields, THE Auth_Service SHALL retrieve the user record from the Database using case-insensitive username comparison
2. IF the user record is retrieved, THEN THE Auth_Service SHALL verify the password against the stored hashed_password using bcrypt
3. IF the password verification succeeds, THEN THE Auth_Service SHALL generate a JWT_Token containing user_id (UUID) and username (string) in the payload with expiration time set to TOKEN_EXPIRY_MINUTES
4. WHEN the JWT_Token is generated, THE Auth_Service SHALL return HTTP status 200 with a JSON response body containing: {"access_token": "<JWT_Token>", "token_type": "bearer"}
5. IF the username does not exist in the Database, THEN THE Auth_Service SHALL return HTTP status 401 with a JSON response body containing: {"detail": "Invalid username or password"}
6. IF the password verification fails, THEN THE Auth_Service SHALL return HTTP status 401 with a JSON response body containing: {"detail": "Invalid username or password"}
7. THE JWT_Token SHALL be signed using a secret key loaded from environment configuration (JWT_SECRET)

### Requirement 3: JWT Token Validation for Protected Endpoints

**User Story:** As a system, I want to validate JWT tokens on protected endpoints, so that only authenticated users can access their movie data.

#### Acceptance Criteria

1. WHEN a request is received for any Movie_Service endpoint, THE System SHALL extract the JWT_Token from the Authorization header using the format "Bearer <token>"
2. IF the Authorization header is missing, THEN THE System SHALL return HTTP status 401 with a JSON response body containing: {"detail": "Not authenticated"}
3. IF the Authorization header does not follow the format "Bearer <token>", THEN THE System SHALL return HTTP status 401 with a JSON response body containing: {"detail": "Invalid authentication credentials"}
4. WHEN the JWT_Token is extracted, THE System SHALL validate the token by verifying: signature using JWT_SECRET, token expiration time has not passed
5. IF the JWT_Token signature is invalid, THEN THE System SHALL return HTTP status 401 with a JSON response body containing: {"detail": "Invalid authentication credentials"}
6. IF the JWT_Token expiration time has passed, THEN THE System SHALL return HTTP status 401 with a JSON response body containing: {"detail": "Token has expired"}
7. WHEN the JWT_Token is validated successfully, THE System SHALL extract the user_id (UUID) from the token payload
8. THE System SHALL use the extracted user_id for all subsequent movie operations without accepting user_id from request body or query parameters

### Requirement 4: Create Movie Entry

**User Story:** As an authenticated user, I want to add a movie to my list with details like title, genre, rating, and notes, so that I can track what I have watched.

#### Acceptance Criteria

1. WHEN a create movie request is received with a validated JWT_Token and title field, THE Movie_Service SHALL create a Movie_Entry record with user_id from the token payload
2. THE Movie_Service SHALL accept optional fields: genre (string, max 100 characters), rating (float between 1.0 and 10.0 inclusive), watched_date (ISO 8601 date string), and notes (string, max 1000 characters)
3. IF the title field is missing or contains only whitespace characters, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Title is required"}
4. IF the title field is longer than 200 characters, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Title must not exceed 200 characters"}
5. IF the genre field is longer than 100 characters, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Genre must not exceed 100 characters"}
6. IF the rating field is provided and is less than 1.0 or greater than 10.0, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Rating must be between 1.0 and 10.0"}
7. IF the notes field is longer than 1000 characters, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Notes must not exceed 1000 characters"}
8. WHEN the Movie_Entry is created successfully, THE Movie_Service SHALL return HTTP status 201 with a JSON response body containing: id (UUID), user_id (UUID), title (string), genre (string or null), rating (float or null), watched_date (ISO 8601 date string or null), notes (string or null), created_at (ISO 8601 timestamp), updated_at (ISO 8601 timestamp). The updated_at field SHALL be set equal to created_at at creation time.
9. IF the Movie_Entry creation fails due to a database error, THEN THE Movie_Service SHALL return HTTP status 500 with a JSON response body containing: {"detail": "Internal server error"}

> **Implementation note:** All 422 validation errors in criteria 3–7 are raised as HTTPException, not Pydantic ValidationError, to maintain consistent `{"detail": "<message>"}` response shape across the API.

### Requirement 5: List Movies with Filtering and Sorting

**User Story:** As an authenticated user, I want to view all my movies with optional filtering and sorting, so that I can find and organize my watch list.

#### Acceptance Criteria

1. WHEN a list movies request is received with a validated JWT_Token, THE Movie_Service SHALL retrieve all Movie_Entry records where user_id matches the authenticated user from the token payload
2. WHERE a genre query parameter is provided, THE Movie_Service SHALL filter results to include only Movie_Entry records where the genre field matches the query parameter value using a case-insensitive comparison (ILIKE in PostgreSQL)
3. WHERE a sort_by query parameter is provided with value "title", THE Movie_Service SHALL sort results by the title field in lexicographical order
4. WHERE a sort_by query parameter is provided with value "watched_date", THE Movie_Service SHALL sort results by the watched_date field in chronological order (null values last)
5. WHERE an order query parameter is provided with value "asc", THE Movie_Service SHALL sort results in ascending order
6. WHERE an order query parameter is provided with value "desc", THE Movie_Service SHALL sort results in descending order
7. WHEN no order parameter is provided, THE Movie_Service SHALL default to ascending order
8. IF the sort_by query parameter is provided with a value other than "title" or "watched_date", THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Invalid sort_by value. Must be 'title' or 'watched_date'"}
9. IF the order query parameter is provided with a value other than "asc" or "desc", THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Invalid order value. Must be 'asc' or 'desc'"}
10. THE Movie_Service SHALL return HTTP status 200 with a JSON array containing Movie_Entry records (each with fields: id, user_id, title, genre, rating, watched_date, notes, created_at, updated_at) belonging only to the authenticated user. An empty array SHALL be returned when the user has no movies.
11. Pagination is out of scope. All movies belonging to the authenticated user are returned in a single response.

### Requirement 6: Retrieve Single Movie Entry

**User Story:** As an authenticated user, I want to view details of a specific movie in my list, so that I can see all the information I stored about it.

#### Acceptance Criteria

1. WHEN a get movie request is received with a validated JWT_Token and movie ID (UUID), THE Movie_Service SHALL retrieve the Movie_Entry record with that ID from the Database
2. FastAPI path parameter type enforcement (UUID type hint) handles invalid UUID format automatically and returns HTTP status 422. No additional manual UUID validation is required.
3. WHEN the Movie_Entry is retrieved, THE Movie_Service SHALL verify that the user_id field matches the authenticated user_id from the JWT_Token payload
4. IF the Movie_Entry exists and the user_id matches the authenticated user, THEN THE Movie_Service SHALL return HTTP status 200 with a JSON response body containing: id (UUID), user_id (UUID), title (string), genre (string or null), rating (float or null), watched_date (ISO 8601 date string or null), notes (string or null), created_at (ISO 8601 timestamp), updated_at (ISO 8601 timestamp)
5. IF the Movie_Entry does not exist in the Database, THEN THE Movie_Service SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
6. IF the Movie_Entry exists but the user_id does not match the authenticated user, THEN THE Movie_Service SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}

### Requirement 7: Update Movie Entry

**User Story:** As an authenticated user, I want to update any details of a movie in my list, so that I can correct or add information over time.

#### Acceptance Criteria

1. WHEN an update movie request is received with a validated JWT_Token and movie ID (UUID), THE Movie_Service SHALL retrieve the Movie_Entry record with that ID from the Database
2. FastAPI path parameter type enforcement (UUID type hint) handles invalid UUID format automatically and returns HTTP status 422. No additional manual UUID validation is required.
3. WHEN the Movie_Entry is retrieved, THE Movie_Service SHALL verify that the user_id field matches the authenticated user_id from the JWT_Token payload
4. IF the Movie_Entry does not exist in the Database, THEN THE Movie_Service SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
5. IF the Movie_Entry exists but the user_id does not match the authenticated user, THEN THE Movie_Service SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
6. IF no fields are provided in the update request body, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "No fields to update"}
7. IF the Movie_Entry exists and belongs to the authenticated user, THEN THE Movie_Service SHALL update only the provided fields from: title (string, max 200 characters), genre (string, max 100 characters), rating (float between 1.0 and 10.0 inclusive), watched_date (ISO 8601 date string), notes (string, max 1000 characters)
8. IF the title field is provided and is longer than 200 characters, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Title must not exceed 200 characters"}
9. IF the notes field is provided and is longer than 1000 characters, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Notes must not exceed 1000 characters"}
10. IF the rating field is provided and is less than 1.0 or greater than 10.0, THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Rating must be between 1.0 and 10.0"}
11. IF the watched_date field is provided and is not in ISO 8601 date format (YYYY-MM-DD), THEN THE Movie_Service SHALL return HTTP status 422 with a JSON response body containing: {"detail": "Invalid date format. Use YYYY-MM-DD"}
12. WHEN fields are updated successfully, THE Movie_Service SHALL update the updated_at timestamp to the current UTC server time
13. WHEN the update completes, THE Movie_Service SHALL return HTTP status 200 with a JSON response body containing the updated movie data: id (UUID), user_id (UUID), title (string), genre (string or null), rating (float or null), watched_date (ISO 8601 date string or null), notes (string or null), created_at (ISO 8601 timestamp), updated_at (ISO 8601 timestamp)

### Requirement 8: Delete Movie Entry

**User Story:** As an authenticated user, I want to remove a movie from my list, so that I can keep my collection current.

#### Acceptance Criteria

1. WHEN a delete movie request is received with a validated JWT_Token and movie ID (UUID), THE Movie_Service SHALL retrieve the Movie_Entry record with that ID from the Database
2. IF the JWT_Token validation fails (missing, invalid signature, or expired), THEN THE System SHALL return HTTP status 401 with the appropriate authentication error message as defined in Requirement 3
3. FastAPI path parameter type enforcement (UUID type hint) handles invalid UUID format automatically and returns HTTP status 422. No additional manual UUID validation is required.
4. WHEN the Movie_Entry is retrieved, THE Movie_Service SHALL verify that the user_id field matches the authenticated user_id from the JWT_Token payload
5. IF the Movie_Entry exists and the user_id matches the authenticated user, THEN THE Movie_Service SHALL delete the record from the Database
6. WHEN the deletion completes successfully, THE Movie_Service SHALL return HTTP status 204 with no response body
7. IF the Movie_Entry does not exist in the Database, THEN THE Movie_Service SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
8. IF the Movie_Entry exists but the user_id does not match the authenticated user, THEN THE Movie_Service SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}

### Requirement 9: Database Schema and Relationships

**User Story:** As a system, I want a properly structured database schema with foreign key relationships, so that data integrity is maintained.

#### Acceptance Criteria

1. THE Database SHALL contain a users table with columns: id (UUID primary key, NOT NULL), username (VARCHAR(50), NOT NULL, UNIQUE), hashed_password (VARCHAR(255), NOT NULL), created_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
2. THE Database SHALL contain a movies table with columns: id (UUID primary key, NOT NULL), user_id (UUID foreign key to users.id, NOT NULL), title (VARCHAR(200), NOT NULL), genre (VARCHAR(100), NULL), rating (FLOAT, NULL), watched_date (DATE, NULL), notes (VARCHAR(1000), NULL), created_at (TIMESTAMP WITH TIME ZONE, NOT NULL), updated_at (TIMESTAMP WITH TIME ZONE, NOT NULL)
3. WHEN a Movie_Entry is created, THE Database SHALL enforce the foreign key constraint requiring a valid user_id that exists in the users table
4. WHEN a user is deleted from the users table, THE Database SHALL delete all Movie_Entry records with matching user_id (ON DELETE CASCADE)
5. THE Database SHALL use UUID type for all primary key fields (users.id, movies.id) and for foreign key fields (movies.user_id)
6. THE Database SHALL enforce uniqueness on the username column in the users table using a case-insensitive index (citext or lowercased indexed column)

### Requirement 10: Database Migration Management

**User Story:** As a developer, I want database migrations managed through Alembic, so that schema changes are version controlled and repeatable.

#### Acceptance Criteria

1. THE System SHALL use Alembic to generate database migration files
2. THE System SHALL use async SQLAlchemy with asyncpg driver for all database operations
3. WHEN a migration is created, THE System SHALL generate migration files in the alembic/versions directory
4. WHEN a migration upgrade is executed, THE System SHALL apply the migration to the database
5. WHEN a migration upgrade completes successfully, THE System SHALL update the alembic_version table with the new revision identifier
6. THE System SHALL provide a downgrade operation for each migration that reverts the schema to the previous state
7. IF a migration upgrade or downgrade fails, THEN THE System SHALL rollback any partial schema changes from that migration

### Requirement 11: Configuration Management

**User Story:** As a system, I want configuration loaded from environment variables, so that sensitive settings are not hardcoded.

#### Acceptance Criteria

1. THE System SHALL load JWT_SECRET, DATABASE_URL, and TOKEN_EXPIRY_MINUTES from environment variables using pydantic-settings. If any required variable is missing, pydantic-settings will raise a ValidationError at startup — no additional custom startup error handling is required.
2. IF JWT_SECRET is shorter than 32 characters, THEN THE System SHALL fail to start. This SHALL be enforced as a field validator in the pydantic-settings Settings class.
3. TOKEN_EXPIRY_MINUTES SHALL be typed as a positive integer in the Settings class. pydantic-settings type coercion is sufficient — no custom range validation is required.
4. THE System SHALL provide a .env.example file containing each required environment variable name, its data type, and an example non-sensitive value
5. THE System SHALL never include JWT_SECRET or hashed passwords in any API response body

### Requirement 12: Password Security

**User Story:** As a system, I want passwords securely hashed and never exposed, so that user credentials are protected.

#### Acceptance Criteria

1. WHEN a password is received during registration or login, THE System SHALL never store or log the plain text password to any persistent storage or log file
2. THE Auth_Service SHALL use bcrypt for password hashing via passlib[bcrypt]. The default work factor provided by passlib is sufficient — do not hardcode a rounds parameter.
3. THE System SHALL never include hashed_password in any API response body or response header
4. WHEN comparing passwords during login, THE Auth_Service SHALL use passlib's verify function to prevent timing attacks
5. IF a login attempt fails for any reason (wrong username or wrong password), THE System SHALL return the same generic error message to avoid revealing whether the username exists
6. Password change functionality is out of scope for this project

### Requirement 13: User Data Isolation

**User Story:** As a user, I want my movie list completely private from other users, so that no one else can view or modify my data.

#### Acceptance Criteria

1. FOR ALL Movie_Service queries (list, retrieve, update, delete), THE System SHALL filter Movie_Entry records by the authenticated user_id from the JWT_Token payload
2. WHEN a create movie request is received, THE System SHALL set the user_id field to the authenticated user_id from the JWT_Token payload
3. WHEN a retrieve, update, or delete movie request is received, THE System SHALL compare the Movie_Entry.user_id with the authenticated user_id before performing the operation
4. THE System SHALL never accept user_id from request body or query parameters for any movie operation
5. IF a user_id is provided in the request body or query parameters, THEN THE System SHALL ignore it and use only the user_id from the JWT_Token payload
6. IF a user attempts to retrieve a Movie_Entry belonging to a different user, THEN THE System SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
7. IF a user attempts to update a Movie_Entry belonging to a different user, THEN THE System SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
8. IF a user attempts to delete a Movie_Entry belonging to a different user, THEN THE System SHALL return HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}

### Requirement 14: API Testing Coverage

**User Story:** As a developer, I want comprehensive automated tests, so that I can verify the API behaves correctly and catch regressions.

#### Acceptance Criteria

1. THE System SHALL include pytest tests using httpx AsyncClient for all authentication and movie endpoints
2. THE tests SHALL verify successful user registration returns HTTP status 201 with a JSON response body containing id (UUID), username (string), and created_at (ISO 8601 timestamp)
3. THE tests SHALL verify successful login returns HTTP status 200 with a JSON response body containing access_token (string) and token_type (string)
4. THE tests SHALL verify login with incorrect credentials (wrong password or non-existent username) returns HTTP status 401 with a JSON response body containing: {"detail": "Invalid username or password"}. Both cases SHALL be covered in a single parametrised test.
5. THE tests SHALL verify creating a movie with valid JWT returns HTTP status 201 with a JSON response body containing all movie fields: id, user_id, title, genre, rating, watched_date, notes, created_at, updated_at
6. THE tests SHALL verify listing movies with valid JWT returns HTTP status 200 with a JSON array containing only the authenticated user's Movie_Entry records
7. THE tests SHALL verify listing movies returns an empty array when the authenticated user has no movies
8. THE tests SHALL verify attempting to fetch another user's Movie_Entry returns HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
9. THE tests SHALL verify attempting to update another user's Movie_Entry returns HTTP status 404 with a JSON response body containing: {"detail": "Movie not found"}
10. THE tests SHALL verify deleting a movie with valid JWT returns HTTP status 204 with no response body
11. THE tests SHALL verify requests to protected endpoints without JWT return HTTP status 401 with a JSON response body containing: {"detail": "Not authenticated"}
12. THE tests SHALL verify creating a movie without title field returns HTTP status 422 with a JSON response body containing: {"detail": "Title is required"}
13. THE tests SHALL use a separate test database configuration to avoid affecting production or development data