---
title: Movie Tracker Backend
inclusion: always
---

# Project overview
A REST API backend for a per-user movie tracking application.
Each user maintains their own private list of movies they have watched.
Users are completely isolated — no sharing, social features, or cross-user access.

# Tech stack
- Package Manager: UV 
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy (async with asyncpg)
- Migrations: Alembic
- Validation: Pydantic v2
- Auth: JWT (python-jose), password hashing with passlib[bcrypt]
- Testing: pytest + httpx (AsyncClient)

# Project structure
movie-tracker/
├── app/
│   ├── main.py             # FastAPI app init, router registration, lifespan
│   ├── database.py         # Async engine, SessionLocal, Base
│   ├── dependencies.py     # get_db(), get_current_user() reusable deps
│   ├── models/
│   │   ├── user.py         # User SQLAlchemy model
│   │   └── movie.py        # Movie SQLAlchemy model
│   ├── schemas/
│   │   ├── user.py         # UserCreate, UserResponse, Token schemas
│   │   └── movie.py        # MovieCreate, MovieUpdate, MovieResponse schemas
│   ├── routers/
│   │   ├── auth.py         # /auth/register, /auth/login
│   │   └── movies.py       # /movies CRUD, all protected
│   └── core/
│       ├── config.py       # Settings via pydantic-settings (.env)
│       └── security.py     # JWT encode/decode, password hash/verify
├── alembic/
│   └── versions/           # Migration files
├── alembic.ini
├── tests/
│   ├── conftest.py         # Test DB setup, async client fixture
│   └── test_movies.py      # Endpoint tests
├── .env.example
└── requirements.txt

# Conventions
- All identifiers: snake_case
- All routes return JSON
- HTTP status codes: 201 for creation, 204 for deletion, 422 for validation errors
- Auth errors: always 401 (never 403 for auth failures)
- Every movies endpoint must call get_current_user() — no unauthenticated movie access
- User passwords are never returned in any response schema
- Pydantic models use `model_config = ConfigDict(from_attributes=True)`
- Keep routers thin: business logic in dependencies or services, not inline in route functions
- Environment variables loaded via `core/config.py` Settings class — no raw os.getenv() calls elsewhere

# Security rules
- Passwords hashed with bcrypt before storage, never stored plain
- JWT secret loaded from environment, never hardcoded
- Every movie record has a user_id FK — always filter queries by the authenticated user's ID
- No endpoint may return another user's data under any circumstance

# Out of scope (do not generate)
- Frontend code or templates
- Admin panels or superuser roles
- Social features (sharing, following, ratings visible to others)
- Email verification or password reset flows
- Docker or deployment configuration
