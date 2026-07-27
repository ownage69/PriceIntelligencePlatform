import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.api.v1.endpoints.tasks import start_single_collection, get_task_status, revoke_task
from app.modules.products.models import Product

@pytest.mark.asyncio
async def test_start_single_collection_success():
    mock_session = AsyncMock()
    mock_product = Product(id=1, name="Test Product")
    mock_session.get.return_value = mock_product
    
    with patch("app.api.v1.endpoints.tasks.collect_product_price.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "test-task-id"
        mock_delay.return_value = mock_task
        
        res = await start_single_collection(product_id=1, session=mock_session)
        
        assert res.task_id == "test-task-id"
        assert res.product_name == "Test Product"
        mock_delay.assert_called_once_with(1)
        mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_start_single_collection_not_found():
    mock_session = AsyncMock()
    mock_session.get.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await start_single_collection(product_id=999, session=mock_session)
        
    assert exc.value.status_code == 404
    mock_session.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_task_status_success():
    with patch("app.api.v1.endpoints.tasks.AsyncResult") as mock_async_result:
        mock_task = MagicMock()
        mock_task.status = "SUCCESS"
        mock_task.info = {"message": "Success! Price saved."}
        mock_async_result.return_value = mock_task
        
        res = await get_task_status(task_id="test-task-id")
        
        assert res.task_id == "test-task-id"
        assert res.status == "SUCCESS"
        assert res.message == "Success! Price saved."
        mock_async_result.assert_called_once()

@pytest.mark.asyncio
async def test_get_task_status_exception():
    with patch("app.api.v1.endpoints.tasks.AsyncResult") as mock_async_result:
        mock_task = MagicMock()
        mock_task.status = "FAILURE"
        mock_task.info = ValueError("Parsing failed due to timeout")
        mock_async_result.return_value = mock_task
        
        res = await get_task_status(task_id="test-task-id")
        
        assert res.task_id == "test-task-id"
        assert res.status == "FAILURE"
        assert res.message == "Parsing failed due to timeout"

@pytest.mark.asyncio
async def test_revoke_task():
    with patch("app.api.v1.endpoints.tasks.celery_app.control.revoke") as mock_revoke:
        res = await revoke_task(task_id="test-task-id")
        
        assert res.status_code == 204
        mock_revoke.assert_called_once_with("test-task-id", terminate=True)
