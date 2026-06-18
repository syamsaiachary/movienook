from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are loaded using pydantic-settings. If required variables
    are missing, pydantic-settings raises ValidationError at startup.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # JWT Configuration
    JWT_SECRET: str = Field(..., description="Secret key for JWT token signing")
    TOKEN_EXPIRY_MINUTES: int = Field(
        default=1440,
        description="JWT token expiry time in minutes"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database URL"
    )
    
    # CORS Configuration
    FRONTEND_URL: str = Field(
        ...,
        description="Frontend URL for CORS configuration"
    )
    
    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret_length(cls, v: str) -> str:
        """
        Validate that JWT_SECRET is at least 32 characters long.
        
        This is kept as explicit security validation, distinct from
        over-engineered startup validation removed elsewhere in the design.
        """
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v


# Global settings instance
settings = Settings()
