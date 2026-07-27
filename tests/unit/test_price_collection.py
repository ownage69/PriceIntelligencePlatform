import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from celery.exceptions import Ignore

from app.workers.tasks.price_collection import (
    _collect_single_product_price,
    collect_product_price,
    _dispatch_due_products,
    collect_active_product_prices
)
from app.modules.products.models import Product
from app.workers.parsers.base import PriceParserError
from app.workers.parsers.schemas import ParsedPrice

@pytest.fixture
def mock_db():
    with patch("app.workers.tasks.price_collection.create_async_engine") as mock_engine_creator, \
         patch("app.workers.tasks.price_collection.async_sessionmaker") as mock_sessionmaker:
        
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        mock_engine_creator.return_value = mock_engine

        mock_session = AsyncMock()
        
        mock_sessionmaker.return_value.return_value.__aenter__.return_value = mock_session
        yield mock_session

@pytest.mark.asyncio
async def test_collect_single_product_ignored(mock_db):
    mock_db.get.return_value = None
    mock_task = MagicMock()
    
    res = await _collect_single_product_price(mock_task, 1)
    
    assert res == {"status": "ignored"}
    mock_task.update_state.assert_called_with(
        state="IGNORED", 
        meta={"message": "The product has been deleted or deactivated."}
    )

@pytest.mark.asyncio
async def test_collect_single_product_success(mock_db):
    mock_product = Product(
        id=1, 
        name="Test Laptop", 
        is_active=True, 
        target_url="http://test.com", 
        target_price=Decimal("200")
    )
    mock_db.get.return_value = mock_product
    mock_task = MagicMock()
    
    with patch("app.workers.tasks.price_collection.httpx.AsyncClient"), \
         patch("app.workers.tasks.price_collection.PriceParserFactory") as mock_factory, \
         patch("app.workers.tasks.price_collection.notification_service") as mock_notify:
        
        mock_notify.notify_price_drop = AsyncMock()
        
        mock_parser = AsyncMock()
        mock_parser.fetch_price.return_value = ParsedPrice(
            price=Decimal("150"), 
            currency="BYN", 
            collected_at=datetime.now(timezone.utc),
            source_url="http://test.com"
        )
        mock_factory.create.return_value = mock_parser
        
        res = await _collect_single_product_price(mock_task, 1)
        
        assert res["status"] == "success"
        assert res["price"] == "150"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_notify.notify_price_drop.assert_called_once()
        
@pytest.mark.asyncio
async def test_collect_single_product_parsing_error(mock_db):
    mock_product = Product(id=1, name="Test", is_active=True, target_url="http://test.com")
    mock_db.get.return_value = mock_product
    mock_task = MagicMock()
    
    with patch("app.workers.tasks.price_collection.httpx.AsyncClient"), \
         patch("app.workers.tasks.price_collection.PriceParserFactory") as mock_factory, \
         patch("app.workers.tasks.price_collection.notification_service") as mock_notify:
        
        mock_notify.notify_parsing_error = AsyncMock()
        
        mock_parser = AsyncMock()
        mock_parser.fetch_price.side_effect = PriceParserError("Test timeout error")
        mock_factory.create.return_value = mock_parser
        
        with pytest.raises(Ignore):
            await _collect_single_product_price(mock_task, 1)
        
        mock_notify.notify_parsing_error.assert_called_once()

@pytest.mark.asyncio
async def test_dispatch_due_products(mock_db):
    mock_product = Product(id=1, is_active=True)
    mock_db.scalars.return_value = [mock_product]
    
    with patch("app.workers.tasks.price_collection.collect_product_price.delay") as mock_delay:
        await _dispatch_due_products()
        mock_delay.assert_called_once_with(1)

def test_collect_product_price_sync_wrapper():
    with patch("app.workers.tasks.price_collection.asyncio.run") as mock_run:
        mock_run.return_value = {"status": "success"}
        res = collect_product_price(1)
        assert res == {"status": "success"}

def test_collect_active_product_prices_sync_wrapper():
    with patch("app.workers.tasks.price_collection.asyncio.run") as mock_run:
        collect_active_product_prices()
        mock_run.assert_called_once()
