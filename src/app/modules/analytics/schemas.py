from decimal import Decimal
from pydantic import BaseModel


class ProductAnalyticsResponse(BaseModel):
    current_price: Decimal | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    avg_price: Decimal | None = None
    total_change_percent: Decimal | None = None
