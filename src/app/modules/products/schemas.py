from datetime import datetime
from decimal import Decimal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Validated payload for adding a product to monitoring."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    target_url: AnyHttpUrl


class ProductRead(BaseModel):
    """Product representation returned by the HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_url: AnyHttpUrl
    is_active: bool


class PriceHistoryRead(BaseModel):
    """A price observation returned by the HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    price: Decimal
    collected_at: datetime
