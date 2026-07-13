from functools import cached_property
from typing import Literal
from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Price Intelligence & Analytics Platform"
    app_env: Literal["development", "test", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    database_host: str = "localhost"
    database_port: int = 5432

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @cached_property
    def database_url(self) -> str:
        password = quote_plus(self.postgres_password.get_secret_value())
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{password}"
            f"@{self.database_host}:{self.database_port}/{self.postgres_db}"
        )

    @cached_property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()