import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.v1.endpoints.tags import (
    create_tag,
    list_tags,
    get_tag,
    update_tag,
    delete_tag,
)
from app.models.catalog import Tag
from app.modules.tags.schemas import TagCreate, TagUpdate

@pytest.mark.asyncio
async def test_create_tag_success():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    
    data = TagCreate(name="electronics")
    res = await create_tag(data=data, session=mock_session)
    
    assert res.name == "electronics"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_list_tags():
    mock_session = AsyncMock()
    mock_session.scalars.return_value = [Tag(id=1, name="electronics")]
    
    res = await list_tags(session=mock_session)
    
    assert len(res) == 1
    assert res[0].name == "electronics"

@pytest.mark.asyncio
async def test_get_tag_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Tag(id=1, name="electronics")
    
    res = await get_tag(tag_id=1, session=mock_session)
    
    assert res.id == 1

@pytest.mark.asyncio
async def test_get_tag_not_found():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await get_tag(tag_id=1, session=mock_session)
        
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_tag_success():
    mock_session = AsyncMock()
    tag_obj = Tag(id=1, name="old")
    mock_session.scalar.return_value = tag_obj
    
    data = TagUpdate(name="new")
    res = await update_tag(tag_id=1, data=data, session=mock_session)
    
    assert res.name == "new"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_delete_tag_success():
    mock_session = AsyncMock()
    mock_session.scalar.return_value = Tag(id=1, name="electronics")
    
    res = await delete_tag(tag_id=1, session=mock_session)
    
    assert res.status_code == 204
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()
