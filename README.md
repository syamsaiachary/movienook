# Movie Tracking API

A FastAPI-based REST API backend for personal movie tracking with JWT authentication.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

3. Update the `.env` file with your database credentials and a secure JWT secret (minimum 32 characters).

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
movienook/
├── app/
│   ├── main.py             # FastAPI app initialization
│   ├── database.py         # Async database engine and session
│   ├── dependencies.py     # Reusable dependencies
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic schemas
│   ├── routers/            # API route handlers
│   └── core/
│       ├── config.py       # Settings configuration
│       └── security.py     # Security utilities
├── alembic/                # Database migrations
├── tests/                  # Test suite
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) + bcrypt (passlib)
- **Testing**: pytest + httpx

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive JWT token

### Movies (Protected)
- `POST /movies` - Create a new movie entry
- `GET /movies` - List all movies (with filtering and sorting)
- `GET /movies/{movie_id}` - Get a specific movie
- `PATCH /movies/{movie_id}` - Update a movie
- `DELETE /movies/{movie_id}` - Delete a movie

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```
