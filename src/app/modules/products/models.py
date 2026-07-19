from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.catalog import Store, Tag
    from app.modules.prices.models import PriceHistory


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    scrape_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        default=60,
        server_default=text("60"),
        nullable=False,
    )
    store_id: Mapped[int | None] = mapped_column(
        ForeignKey("stores.id", ondelete="SET NULL"),
        nullable=True,
    )

    price_history: Mapped[list[PriceHistory]] = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    store: Mapped[Store | None] = relationship("Store", back_populates="products")
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary="product_tags",
        back_populates="products",
    )
