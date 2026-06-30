"""API configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """Global configuration for the FastAPI service."""

    NCE_CONSTITUTION_PATH: str = "examples/constitution.yaml"
    API_TITLE: str = "Neural Constitution Engine API"
    API_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://nce_user:nce_password@localhost:5434/nce_db"

    # Security
    SECRET_KEY: str = "SUPER_SECRET_KEY_FOR_JWT_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = APISettings()
