# app/core/config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Diagnostic Assistant API"
    PROJECT_DESCRIPTION: str = "API for AI-powered medical diagnostics"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Database settings
    DB_USER: str 
    DB_PASS: str 
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

__all__ = ["settings"]