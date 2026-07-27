import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from .exceptions import (
    TelegramAPIError,
    TelegramAuthError,
    TelegramBadRequestError,
    TelegramNetworkError,
    TelegramRateLimitError,
)

logger = logging.getLogger(__name__)


class TelegramClient:

    @retry(
        retry=retry_if_exception_type((TelegramNetworkError, TelegramRateLimitError, TelegramAPIError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    async def _make_request(self, method_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not settings.telegram_bot_token:
            logger.warning("Telegram bot token is missing. Request skipped.")
            return {}

        token = settings.telegram_bot_token.get_secret_value()
        url = f"https://api.telegram.org/bot{token}/{method_name}"
        timeout = getattr(settings, "telegram_timeout_seconds", 15.0)

        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
            try:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    return response.json()

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Telegram Rate Limit (429) hit. Retry after {retry_after}s.")
                    raise TelegramRateLimitError("Rate limit exceeded", retry_after=retry_after)

                if response.status_code in (401, 404):
                    logger.error("Telegram API authentication failed (invalid token).")
                    raise TelegramAuthError("Invalid Telegram token.")

                if response.status_code == 400:
                    logger.error(f"Telegram API Bad Request (400): {response.text}")
                    raise TelegramBadRequestError(f"Bad Request: {response.text}")

                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                logger.error(f"Telegram API HTTP error {e.response.status_code}: {e.response.text}")
                raise TelegramAPIError(f"API Error {e.response.status_code}") from e
                
            except httpx.RequestError as e:
                logger.error(f"Telegram network connection error: {e}")
                raise TelegramNetworkError(f"Network error: {e}") from e

        return {}

    async def send_message(self, chat_id: str | int, text: str, **kwargs) -> dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "text": text,
            **kwargs
        }
        return await self._make_request("sendMessage", payload)

    async def send_photo(self, chat_id: str | int, photo_url: str, caption: str = "", **kwargs) -> dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            **kwargs
        }
        return await self._make_request("sendPhoto", payload)
