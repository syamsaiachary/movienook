"""Main entry point for the movienook application."""

from fastapi import FastAPI
from app.routers import auth

# Create FastAPI application instance
app = FastAPI(
    title="Movie Tracking API",
    description="REST API for personal movie tracking",
    version="1.0.0"
)

# Register routers
app.include_router(auth.router)


def main():
    print("Hello from movienook!")


if __name__ == "__main__":
    main()
