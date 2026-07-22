from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from decimal import Decimal

import httpx
from pydantic import ValidationError
from sqlalchemy import func, literal_column, or_, pool, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.db.models
from app.core.config import settings
from app.modules.prices.models import PriceHistory
from app.modules.products.models import Product
from app.workers.celery_app import celery_app
from app.workers.parsers.base import PriceParserError
from app.workers.parsers.factory import PriceParserFactory

from celery.exceptions import Ignore

logger = logging.getLogger(__name__)


async def _collect_single_product_price(task, product_id: int) -> dict:
    engine = create_async_engine(settings.database_url, poolclass=pool.NullPool)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with session_factory() as session:

            product = await session.get(Product, product_id)
            if not product or not product.is_active:
                task.update_state(state="IGNORED", meta={"message": "The product has been deleted or deactivated."})
                return {"status": "ignored"}

            task.update_state(state="INITIALIZING", meta={"message": "Initializing an invisible browser..."})
            
            timeout = httpx.Timeout(15.0, connect=5.0)
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers={"User-Agent": "PriceIntelligenceBot/0.1"},
                timeout=timeout,
            ) as client:
                task.update_state(state="NAVIGATING", meta={"message": f"Going to the product page..."})
                
                try:
                    parser = PriceParserFactory.create(url=product.target_url, client=client)
                    
                    task.update_state(state="PARSING", meta={"message": "Analyzing and looking for the price..."})
                    parsed_price = await parser.fetch_price()
                    
                except (httpx.HTTPError, PriceParserError, ValidationError) as error:
                    logger.warning("Price collection failed for product_id=%s: %s", product.id, error)
                    task.update_state(state="FAILURE", meta={"message": f"Parsing error (site protection failed or selector was not found): {error}"})
                    raise Ignore() 

                history_row = PriceHistory(
                    product_id=product.id,
                    price=parsed_price.price,
                    collected_at=parsed_price.collected_at,
                )
                session.add(history_row)
                await session.commit()

                success_msg = f"Success! The price has been saved: {parsed_price.price} {parsed_price.currency}"
                task.update_state(state="SUCCESS", meta={"message": success_msg})
                
                return {"status": "success", "price": str(parsed_price.price)}
    finally:
        await engine.dispose()


@celery_app.task(bind=True, name="price_collection.collect_product_price")
def collect_product_price(self, product_id: int) -> dict:
    return asyncio.run(_collect_single_product_price(self, product_id))


async def _dispatch_due_products() -> None:
    engine = create_async_engine(settings.database_url, poolclass=pool.NullPool)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with session_factory() as session:
            last_collected_at = (
                select(func.max(PriceHistory.collected_at))
                .where(PriceHistory.product_id == Product.id)
                .correlate(Product)
                .scalar_subquery()
            )
            one_minute = literal_column("INTERVAL '1 minute'")
            products = await session.scalars(
                select(Product)
                .where(
                    Product.is_active.is_(True),
                    or_(
                        last_collected_at.is_(None),
                        func.now() >= last_collected_at + Product.scrape_interval_minutes * one_minute,
                    ),
                )
                .with_for_update(skip_locked=True)
            )
            
            for product in products:
                collect_product_price.delay(product.id)
    finally:
        await engine.dispose()


@celery_app.task(name="price_collection.collect_active_product_prices")
def collect_active_product_prices() -> None:
    asyncio.run(_dispatch_due_products())
