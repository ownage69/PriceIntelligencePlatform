import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_telegram_notification(message: str) -> None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.debug("Telegram bot token or chat ID is not set. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info("Telegram notification sent successfully.")
        except httpx.HTTPError as error:
            logger.error(f"Failed to send Telegram message: {error}")
