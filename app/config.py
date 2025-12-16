"""Application configuration using Pydantic Settings.

Configuration values can be overridden via environment variables.
For example, to change the host: export HOST=0.0.0.0

Supports loading from .env file for local development.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
class Settings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be overridden via environment variables.
    For example: HOST=0.0.0.0 PORT=9000 python -m app.main
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # API Settings
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    environment: str = "development"

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"

    # LLM Settings (for future real LLM integration)
    llm_provider: str = "mock"  # mock | vercel | openai | anthropic
    llm_api_key: str = ""
    llm_model: str = "gpt-4"


# Global settings instance
settings = Settings()
