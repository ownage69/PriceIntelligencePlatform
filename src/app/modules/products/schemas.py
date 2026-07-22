from datetime import datetime
from decimal import Decimal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.modules.categories.schemas import CategoryRead
from app.modules.stores.schemas import StoreRead
from app.modules.tags.schemas import TagRead


class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    target_url: AnyHttpUrl
    scrape_interval_minutes: int = Field(default=60, ge=1)


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    target_url: AnyHttpUrl | None = None
    is_active: bool | None = None
    scrape_interval_minutes: int | None = Field(default=None, ge=1)
    store_id: int | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class ProductWithRelationsCreate(ProductCreate):
    store_id: int | None = None
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)


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
    created_at: datetime
    scrape_interval_minutes: int
    store: StoreRead | None = None
    category: CategoryRead | None = None
    tags: list[TagRead] = Field(default_factory=list)


class PriceHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    price: Decimal
    collected_at: datetime
