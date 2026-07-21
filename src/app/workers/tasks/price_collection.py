from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import TypedDict

import httpx
from pydantic import ValidationError
from sqlalchemy import func, insert, literal_column, or_, pool, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.db.models

from app.core.config import settings
from app.modules.prices.models import PriceHistory
from app.modules.products.models import Product
from app.workers.celery_app import celery_app
from app.workers.parsers.base import PriceParserError
from app.workers.parsers.factory import PriceParserFactory

logger = logging.getLogger(__name__)


class CollectionStats(TypedDict):

    processed: int
    saved: int
    failed: int


async def _get_due_active_products(session: AsyncSession) -> Sequence[Product]:
    last_collected_at = (
        select(func.max(PriceHistory.collected_at))
        .where(PriceHistory.product_id == Product.id)
        .correlate(Product)
        .scalar_subquery()
    )
    one_minute = literal_column("INTERVAL '1 minute'")
    result = await session.scalars(
        select(Product)
        .where(
            Product.is_active.is_(True),
            or_(
                last_collected_at.is_(None),
                func.now()
                >= last_collected_at
                + Product.scrape_interval_minutes * one_minute,
            ),
        )
        .order_by(Product.id)
        .with_for_update(skip_locked=True)
    )
    return result.all()


async def _collect_active_product_prices() -> CollectionStats:
    statistics: CollectionStats = {"processed": 0, "saved": 0, "failed": 0}
    history_rows: list[dict[str, int | Decimal | datetime]] = []

    engine = create_async_engine(settings.database_url, poolclass=pool.NullPool)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with session_factory() as session:
            products = await _get_due_active_products(session)
            timeout = httpx.Timeout(15.0, connect=5.0)

            async with httpx.AsyncClient(
                follow_redirects=True,
                headers={"User-Agent": "PriceIntelligenceBot/0.1"},
                timeout=timeout,
            ) as client:
                for product in products:
                    statistics["processed"] += 1
                    try:
                        parser = PriceParserFactory.create(url=product.target_url, client=client)
                        parsed_price = await parser.fetch_price()
                    except (
                        httpx.HTTPError,
                        PriceParserError,
                        ValidationError,
                    ) as error:
                        statistics["failed"] += 1
                        logger.warning(
                            "Price collection failed for product_id=%s: %s",
                            product.id,
                            error,
                        )
                        continue

                    history_rows.append(
                        {
                            "product_id": product.id,
                            "price": parsed_price.price,
                            "collected_at": parsed_price.collected_at,
                        }
                    )

            if history_rows:
                await session.execute(insert(PriceHistory), history_rows)
                await session.commit()
                statistics["saved"] = len(history_rows)
    finally:
        await engine.dispose()

    return statistics


@celery_app.task(name="price_collection.collect_active_product_prices")
def collect_active_product_prices() -> CollectionStats:
    return asyncio.run(_collect_active_product_prices())
