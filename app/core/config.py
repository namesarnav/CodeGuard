"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    # Application
    app_name: str = "CodeGuard AI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(
        default="change-me-in-production-minimum-32-characters-long",
        min_length=32,
        description="Secret key for JWT tokens and encryption (must be at least 32 characters)",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://codeguard:codeguard@localhost:5432/codeguard",
        description="PostgreSQL connection URL",
    )
    postgres_user: str = "codeguard"
    postgres_password: str = "codeguard"
    postgres_db: str = "codeguard"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "codeguard_embeddings"

    # LLM - Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codellama:34b-instruct"
    ollama_fallback_model: str = "deepseek-coder:33b"

    # LLM - OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    use_openai_fallback: bool = False

    # GitHub
    github_app_id: str | None = None
    github_app_private_key: str | None = None
    github_pat: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_callback_url: str = "http://localhost:3000/auth/callback"

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # S3
    s3_bucket_name: str = "codeguard-reports"
    s3_region: str = "us-east-1"

    # Frontend
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    max_file_size_mb: int = 100
    max_scan_duration_seconds: int = 3600

    @field_validator("cors_origins", "allowed_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key and warn if using default."""
        if v == "change-me-in-production-minimum-32-characters-long":
            import warnings
            warnings.warn(
                "Using default SECRET_KEY! Change this in production for security.",
                UserWarning,
                stacklevel=2,
            )
        return v

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.database_url.replace("postgresql+asyncpg", "postgresql")

    @property
    def qdrant_url(self) -> str:
        """Get Qdrant connection URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

