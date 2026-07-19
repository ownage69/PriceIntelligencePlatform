from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.api.v1.endpoints.products import (
    get_active_products, 
    create_product,
    bulk_create_products,
    list_active_products,
    list_product_price_history,
    create_product_with_relations,
    delete_product,
    product_cache,
    update_product,
)
from app.modules.products.models import Product
from app.modules.prices.models import PriceHistory
from app.models.catalog import Tag
from app.modules.products.schemas import ProductBulkCreate, ProductCreate, ProductUpdate, ProductWithRelationsCreate
from app.core.exceptions import ProductAlreadyExistsError, ProductNotFoundError

@pytest.mark.asyncio
async def test_get_active_products_success():
    mock_session = AsyncMock()
    mock_product_1 = Product(id=1, name="Mocked Laptop", is_active=True)
    mock_product_2 = Product(id=2, name="Mocked Mouse", is_active=True)
    
    mock_session.scalar.return_value = 2 
    mock_session.scalars.return_value = [mock_product_1, mock_product_2]

    total, items = await get_active_products(session=mock_session, page=1, size=50)

    assert total == 2
    assert len(items) == 2
    assert items[0].name == "Mocked Laptop"
    
    mock_session.scalar.assert_called_once()
    mock_session.scalars.assert_called_once()

@pytest.mark.asyncio
async def test_get_active_products_with_filters():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = 1
    mock_session.scalars.return_value = [Product(id=1, name="Test", is_active=True)]

    total, items = await get_active_products(
        session=mock_session, 
        page=1, 
        size=50, 
        store_name="amaz", 
        tag_name="elec"
    )

    assert total == 1
    assert len(items) == 1

@pytest.mark.asyncio
async def test_get_active_products_empty():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    mock_session.scalars.return_value = []

    total, items = await get_active_products(session=mock_session)
    assert total == 0
    assert len(items) == 0

@pytest.mark.asyncio
async def test_create_product_success():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.expunge_all = MagicMock()
    
    mock_session.scalar.return_value = Product(
        id=1, name="P1", target_url="http://x.com", is_active=True
    )
    
    product_in = ProductCreate(name="P1", target_url="http://x.com")
    res = await create_product(product_in=product_in, session=mock_session)
    
    assert res.name == "P1"
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_product_rolls_back_on_integrity_error():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.expunge_all = MagicMock()
    
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    product_in = ProductCreate(name="Duplicate", target_url="https://ex.com/dup")

    with pytest.raises(ProductAlreadyExistsError):
        await create_product(product_in=product_in, session=mock_session)
    
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_bulk_create_products_success():
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    
    data = ProductBulkCreate(target_urls=["http://url1.com", "http://url2.com"])
    
    result = await bulk_create_products(data=data, session=mock_session)
    
    assert result.added_count == 2
    mock_session.add_all.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_bulk_create_products_integrity_error():
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    data = ProductBulkCreate(target_urls=["http://url1.com"])
    
    with pytest.raises(ProductAlreadyExistsError):
        await bulk_create_products(data=data, session=mock_session)
        
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_list_active_products_uses_cache():
    mock_session = AsyncMock()
    product_cache.invalidate()
    
    mock_product = Product(
        id=1, 
        name="Test", 
        target_url="https://test.com", 
        is_active=True,
        created_at=datetime.now(timezone.utc),
        scrape_interval_minutes=60,
        store=None,
        tags=[]
    )
    
    with patch("app.api.v1.endpoints.products.get_active_products") as mock_get:
        mock_get.return_value = (1, [mock_product])
        
        res1 = await list_active_products(session=mock_session)
        res2 = await list_active_products(session=mock_session)
        
        assert res1.total_items == 1
        assert res2.total_items == 1
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_list_product_price_history_not_found():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    
    with pytest.raises(ProductNotFoundError):
        await list_product_price_history(product_id=999, session=mock_session)

@pytest.mark.asyncio
async def test_list_product_price_history_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Product(id=1)
    mock_session.scalars.return_value = [PriceHistory(id=1, price=100.0)]
    
    res = await list_product_price_history(product_id=1, session=mock_session)
    
    assert len(res) == 1
    mock_session.scalars.assert_called_once()

@pytest.mark.asyncio
async def test_create_product_with_relations_success():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.expunge_all = MagicMock()
    
    mock_session.scalars.return_value = [Tag(id=1)]
    mock_session.scalar.return_value = Product(
        id=1, name="P1", target_url="http://x.com", is_active=True, tags=[Tag(id=1)]
    )
    
    data = ProductWithRelationsCreate(name="P1", target_url="http://x.com", store_id=1, tag_ids=[1])
    
    res = await create_product_with_relations(data=data, session=mock_session)
    
    assert res.name == "P1"
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_product_with_relations_missing_tags():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    
    mock_session.scalars.return_value = []
    
    data = ProductWithRelationsCreate(name="P1", target_url="http://x.com", store_id=1, tag_ids=[1, 2])
    
    with pytest.raises(HTTPException):
        await create_product_with_relations(data=data, session=mock_session)
        
    mock_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_create_product_with_relations_integrity_error():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.scalars.return_value = []
    
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    data = ProductWithRelationsCreate(name="P1", target_url="http://x.com", store_id=1, tag_ids=[])
    
    with pytest.raises(ProductAlreadyExistsError):
        await create_product_with_relations(data=data, session=mock_session)
        
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_product_success():
    mock_session = AsyncMock()
    product = Product(id=1, name="Before", target_url="https://example.com/old")
    updated_product = Product(id=1, name="After", target_url="https://example.com/new")
    mock_session.scalar.side_effect = [product, updated_product]

    result = await update_product(
        product_id=1,
        product_in=ProductUpdate(
            name="After",
            target_url="https://example.com/new",
            scrape_interval_minutes=10,
            tag_ids=[],
        ),
        session=mock_session,
    )

    assert result.name == "After"
    assert product.scrape_interval_minutes == 10
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_product_success():
    mock_session = AsyncMock()
    product = Product(id=1, name="Product", target_url="https://example.com/product")
    mock_session.get.return_value = product

    response = await delete_product(product_id=1, session=mock_session)

    assert response.status_code == 204
    mock_session.delete.assert_awaited_once_with(product)
    mock_session.commit.assert_called_once()
