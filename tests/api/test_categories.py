import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError

from app.api.v1.endpoints.categories import (
    create_category,
    list_categories,
    get_category,
    update_category,
    delete_category,
)
from app.models.category import Category
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate
from app.core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError

@pytest.mark.asyncio
async def test_create_category_success():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    
    data = CategoryCreate(name="Notebooks")
    res = await create_category(data=data, session=mock_session)
    
    assert res.name == "Notebooks"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_category_integrity_error():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    data = CategoryCreate(name="Notebooks")
    with pytest.raises(CategoryAlreadyExistsError):
        await create_category(data=data, session=mock_session)
        
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_list_categories():
    mock_session = AsyncMock()
    mock_session.scalars.return_value = [Category(id=1, name="Notebooks")]
    
    res = await list_categories(session=mock_session)
    
    assert len(res) == 1
    assert res[0].name == "Notebooks"

@pytest.mark.asyncio
async def test_get_category_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Category(id=1, name="Notebooks")
    
    res = await get_category(category_id=1, session=mock_session)
    
    assert res.id == 1

@pytest.mark.asyncio
async def test_get_category_not_found():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    
    with pytest.raises(CategoryNotFoundError):
        await get_category(category_id=999, session=mock_session)

@pytest.mark.asyncio
async def test_update_category_success():
    mock_session = AsyncMock()
    cat_obj = Category(id=1, name="Old name")
    mock_session.scalar.return_value = cat_obj
    
    data = CategoryUpdate(name="New name")
    res = await update_category(category_id=1, data=data, session=mock_session)
    
    assert res.name == "New name"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_update_category_integrity_error():
    mock_session = AsyncMock()
    cat_obj = Category(id=1, name="Old name")
    mock_session.scalar.return_value = cat_obj
    mock_session.commit.side_effect = IntegrityError("...", {}, Exception())
    
    data = CategoryUpdate(name="Already exists")
    with pytest.raises(CategoryAlreadyExistsError):
        await update_category(category_id=1, data=data, session=mock_session)
        
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_delete_category_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Category(id=1, name="Notebooks")
    
    res = await delete_category(category_id=1, session=mock_session)
    
    assert res.status_code == 204
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
