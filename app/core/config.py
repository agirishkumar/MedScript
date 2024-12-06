# app/core/config.py

'''
This module contains the configuration for the app.
'''

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class defines the configuration settings for the application, including project name, description, version, API version, allowed origins, database settings, and JWT settings.

    Attributes:
        PROJECT_NAME (str): The name of the project.
        PROJECT_DESCRIPTION (str): The description of the project.
        PROJECT_VERSION (str): The version of the project.
        API_V1_STR (str): The API version string.
        ALLOWED_ORIGINS (List[str]): The list of allowed origins.
        DB_USER (str): The username for the database.
        DB_PASS (str): The password for the database.
        DB_NAME (str): The name of the database.
        DB_HOST (str): The host of the database.
        DB_PORT (str): The port of the database.
        JWT_SECRET_KEY (str): The secret key for JWT.
        JWT_REFRESH_SECRET_KEY (str): The refresh secret key for JWT.
    """
    PROJECT_NAME: str = "Medical Diagnostic Assistant API"
    PROJECT_DESCRIPTION: str = "API for AI-powered medical diagnostics"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # API URL
    BASE_API_URL: str

    # Database settings
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    # Airflow settings
    AIRFLOW_UID: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    AIRFLOW_WWW_USER_USERNAME: str
    AIRFLOW_WWW_USER_PASSWORD: str

    # GCP Settings
    CLOUD_SQL_INSTANCE: str
    GOOGLE_APPLICATION_CREDENTIALS: str

    BASE_API_URL: str

    class Config:
        """
        Configuration settings for the Settings class.

        This class defines the configuration settings for the Settings class,
        including the environment file and case sensitivity.
    """
        env_file = ".env"
        case_sensitive = True


settings = Settings()

__all__ = ["settings"]
