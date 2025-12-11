from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator

load_dotenv()


class Settings(BaseSettings):
    # App Info
    TITLE: str = "GenAI API"
    DESCRIPTION: str = "Blog API Powered by Generative AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_MINUTES: int = 24 * 60
    REMEMBER_ME_REFRESH_TOKEN_EXPIRES_MINUTES: int = 30 * 24 * 60  # 30 days for "remember me"
    REFRESH_TOKEN_ROTATION: bool = True

    # Cookie Configuration
    SECURE_COOKIE: bool = False  # Set to True in production (requires HTTPS)
    COOKIE_DOMAIN: Optional[str] = None  # None for same-origin only
    ACCESS_COOKIE_MAX_AGE: int = 15 * 60  # 15 minutes in seconds
    REFRESH_COOKIE_MAX_AGE: int = 7 * 24 * 60 * 60  # 7 days in seconds
    COOKIE_SAMESITE: str = "lax"  # CSRF protection

    # Server
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    # Email
    EMAIL_HOST: str = ""
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "Pass123"
    REDIS_DB: int = 0

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


settings = Settings()
