import pytest
from unittest.mock import patch, MagicMock

from app.api.v1.endpoints.tasks import start_price_collection, get_task_status

@pytest.mark.asyncio
async def test_start_price_collection():
    with patch("app.api.v1.endpoints.tasks.collect_active_product_prices.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "test-task-id"
        mock_delay.return_value = mock_task
        
        res = await start_price_collection()
        
        assert res.task_id == "test-task-id"
        mock_delay.assert_called_once()

@pytest.mark.asyncio
async def test_get_task_status():
    with patch("app.api.v1.endpoints.tasks.AsyncResult") as mock_async_result:
        mock_task = MagicMock()
        mock_task.status = "SUCCESS"
        mock_async_result.return_value = mock_task
        
        res = await get_task_status(task_id="test-task-id")
        
        assert res.task_id == "test-task-id"
        assert res.status == "SUCCESS"
        mock_async_result.assert_called_once()
