import logging
from decimal import Decimal

from app.core.config import settings
from .client import TelegramClient
from .templates import TelegramTemplates
from .exceptions import TelegramBaseError

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    
    def __init__(self):
        self._client = TelegramClient()
        self._chat_id = settings.telegram_chat_id

    async def _send_notification(self, text: str) -> None:
        if not self._chat_id:
            return
            
        try:
            await self._client.send_message(
                chat_id=self._chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except TelegramBaseError as e:
            logger.error(f"TelegramBaseError: {e}")
        except Exception as e:
            logger.exception(f"Exception: {e}")

    async def notify_price_drop(
        self, 
        product_name: str, 
        product_url: str, 
        current_price: Decimal, 
        target_price: Decimal, 
        currency: str
    ) -> None:
        text, _ = TelegramTemplates.target_price_reached(
            product_name=product_name,
            product_url=product_url,
            current_price=current_price,
            target_price=target_price,
            currency=currency
        )
        await self._send_notification(text)

    async def notify_parsing_error(
        self, 
        product_id: int, 
        product_url: str, 
        error_message: str
    ) -> None:
        text, _ = TelegramTemplates.parsing_error(
            product_id=product_id,
            product_url=product_url,
            error_message=error_message
        )
        await self._send_notification(text)


notification_service = TelegramNotificationService()
