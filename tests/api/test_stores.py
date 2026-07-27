import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError

from app.api.v1.endpoints.stores import (
    create_store,
    list_stores,
    get_store,
    update_store,
    delete_store,
)
from app.models.catalog import Store
from app.modules.stores.schemas import StoreCreate, StoreUpdate
from app.core.exceptions import StoreAlreadyExistsError, StoreNotFoundError

@pytest.mark.asyncio
async def test_create_store_success():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    
    data = StoreCreate(name="Test Store", domain="test.com")
    res = await create_store(data=data, session=mock_session)
    
    assert res.name == "Test Store"
    assert res.domain == "test.com"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_store_integrity_error():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    data = StoreCreate(name="Test Store", domain="test.com")
    with pytest.raises(StoreAlreadyExistsError):
        await create_store(data=data, session=mock_session)
        
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_list_stores():
    mock_session = AsyncMock()
    mock_session.scalars.return_value = [Store(id=1, name="S1", domain="d1.com")]
    
    res = await list_stores(session=mock_session)
    
    assert len(res) == 1
    assert res[0].name == "S1"

@pytest.mark.asyncio
async def test_get_store_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Store(id=1, name="S1", domain="d1.com")
    
    res = await get_store(store_id=1, session=mock_session)
    
    assert res.id == 1

@pytest.mark.asyncio
async def test_get_store_not_found():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    
    with pytest.raises(StoreNotFoundError):
        await get_store(store_id=1, session=mock_session)

@pytest.mark.asyncio
async def test_update_store_success():
    mock_session = AsyncMock()
    store_obj = Store(id=1, name="Old", domain="old.com")
    mock_session.scalar.return_value = store_obj
    
    data = StoreUpdate(name="New")
    res = await update_store(store_id=1, data=data, session=mock_session)
    
    assert res.name == "New"
    assert res.domain == "old.com"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_update_store_integrity_error():
    mock_session = AsyncMock()
    store_obj = Store(id=1, name="Old", domain="old.com")
    mock_session.scalar.return_value = store_obj
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    data = StoreUpdate(domain="exists.com")
    with pytest.raises(StoreAlreadyExistsError):
        await update_store(store_id=1, data=data, session=mock_session)
        
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_delete_store_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Store(id=1, name="S1", domain="d1.com")
    
    res = await delete_store(store_id=1, session=mock_session)
    
    assert res.status_code == 204
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
