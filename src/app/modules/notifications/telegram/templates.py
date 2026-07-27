import html
from decimal import Decimal
from enum import Enum

class NotificationType(str, Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TelegramTemplates:

    @staticmethod
    def _escape(text: str) -> str:
        return html.escape(str(text))

    @classmethod
    def target_price_reached(
        cls, 
        product_name: str, 
        product_url: str, 
        current_price: Decimal, 
        target_price: Decimal, 
        currency: str
    ) -> tuple[str, NotificationType]:
        safe_name = cls._escape(product_name)
        safe_url = cls._escape(product_url)
        
        text = (
            f"🔥 <b>Target Price Reached!</b>\n\n"
            f"📦 <b>Product:</b> <a href='{safe_url}'>{safe_name}</a>\n"
            f"💰 <b>Current Price:</b> <b>{current_price} {currency}</b>\n"
            f"🎯 <b>Target Price:</b> {target_price} {currency}"
        )
        return text, NotificationType.SUCCESS

    @classmethod
    def price_drop(
        cls,
        product_name: str,
        product_url: str,
        old_price: Decimal,
        new_price: Decimal,
        currency: str
    ) -> tuple[str, NotificationType]:
        safe_name = cls._escape(product_name)
        safe_url = cls._escape(product_url)
        
        text = (
            f"📉 <b>Price Dropped!</b>\n\n"
            f"📦 <b>Product:</b> <a href='{safe_url}'>{safe_name}</a>\n"
            f"🏷 <b>Old Price:</b> {old_price} {currency}\n"
            f"💰 <b>New Price:</b> <b>{new_price} {currency}</b>"
        )
        return text, NotificationType.INFO

    @classmethod
    def parsing_error(
        cls, 
        product_id: int, 
        product_url: str, 
        error_message: str
    ) -> tuple[str, NotificationType]:
        safe_url = cls._escape(product_url)
        safe_error = cls._escape(error_message)
        
        text = (
            f"⚠️ <b>Parsing Error</b>\n\n"
            f"🆔 <b>Product ID:</b> {product_id}\n"
            f"🔗 <b>URL:</b> <a href='{safe_url}'>Visit Site</a>\n"
            f"❌ <b>Details:</b> <code>{safe_error}</code>"
        )
        return text, NotificationType.ERROR

    @classmethod
    def critical_error(cls, error_title: str, error_details: str) -> tuple[str, NotificationType]:
        safe_title = cls._escape(error_title)
        safe_details = cls._escape(error_details)
        
        text = (
            f"🚨 <b>CRITICAL ERROR</b>\n\n"
            f"📌 <b>Event:</b> {safe_title}\n"
            f"📜 <b>Description:</b> <code>{safe_details}</code>"
        )
        return text, NotificationType.CRITICAL

    @classmethod
    def new_product(cls, product_name: str, product_url: str) -> tuple[str, NotificationType]:
        safe_name = cls._escape(product_name)
        safe_url = cls._escape(product_url)
        
        text = (
            f"✨ <b>New Product Added</b>\n\n"
            f"📦 <b>Name:</b> <a href='{safe_url}'>{safe_name}</a>"
        )
        return text, NotificationType.SUCCESS

    @classmethod
    def parsing_finished(cls, total_success: int, total_failed: int) -> tuple[str, NotificationType]:
        text = (
            f"📊 <b>Price Collection Finished</b>\n\n"
            f"✅ Successfully processed: <b>{total_success}</b>\n"
            f"❌ Parsing errors: <b>{total_failed}</b>"
        )
        return text, NotificationType.INFO
