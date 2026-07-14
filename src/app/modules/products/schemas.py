from datetime import datetime
from decimal import Decimal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    target_url: AnyHttpUrl


class ProductBulkCreate(BaseModel):
    target_urls: list[AnyHttpUrl]


class BulkCreateResponse(BaseModel):
    added_count: int


class ProductRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_url: AnyHttpUrl
    is_active: bool


class PriceHistoryRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    price: Decimal
    collected_at: datetime
