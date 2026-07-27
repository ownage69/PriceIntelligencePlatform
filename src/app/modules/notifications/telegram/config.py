from pydantic import SecretStr

from app.core.config import settings


class TelegramConfig:

    @property
    def bot_token(self) -> SecretStr | None:
        return settings.telegram_bot_token

    @property
    def chat_id(self) -> str | None:
        return settings.telegram_chat_id

    @property
    def timeout_seconds(self) -> float:
        return getattr(settings, "telegram_timeout_seconds", 15.0)

    @property
    def max_retries(self) -> int:
        return getattr(settings, "telegram_max_retries", 5)

    @property
    def backoff_min_seconds(self) -> int:
        return getattr(settings, "telegram_backoff_min_seconds", 2)

    @property
    def backoff_max_seconds(self) -> int:
        return getattr(settings, "telegram_backoff_max_seconds", 30)

    @property
    def pool_max_keepalive_connections(self) -> int:
        return getattr(settings, "telegram_pool_max_keepalive_connections", 20)

    @property
    def pool_max_connections(self) -> int:
        return getattr(settings, "telegram_pool_max_connections", 100)

    @property
    def pool_keepalive_expiry(self) -> float:
        return getattr(settings, "telegram_pool_keepalive_expiry", 30.0)


telegram_config = TelegramConfig()
