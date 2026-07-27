import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.modules.analytics.service import analytics_service

@pytest.mark.asyncio
async def test_get_product_price_dynamics_empty_history():
    mock_session = AsyncMock()
    
    mock_stats_result = MagicMock()
    mock_stats_result.first.return_value = MagicMock(min_price=None, max_price=None, avg_price=None)
    
    mock_history_result = MagicMock()
    mock_history_result.scalars().all.return_value = []
    
    mock_session.execute.side_effect = [mock_stats_result, mock_history_result]
    
    res = await analytics_service.get_product_price_dynamics(session=mock_session, product_id=1)
    
    assert res == {}
    assert mock_session.execute.call_count == 2

@pytest.mark.asyncio
async def test_get_product_price_dynamics_with_data():
    mock_session = AsyncMock()
    
    mock_stats_result = MagicMock()
    mock_stats_result.first.return_value = MagicMock(
        min_price=Decimal("100"), 
        max_price=Decimal("200"), 
        avg_price=Decimal("150.555")
    )
    
    mock_history_result = MagicMock()
    mock_history_result.scalars().all.return_value = [Decimal("200"), Decimal("150"), Decimal("100")]
    
    mock_session.execute.side_effect = [mock_stats_result, mock_history_result]
    
    res = await analytics_service.get_product_price_dynamics(session=mock_session, product_id=1)
    
    assert res["current_price"] == Decimal("100")
    assert res["min_price"] == Decimal("100")
    assert res["max_price"] == Decimal("200")
    assert res["avg_price"] == Decimal("150.56") 
    assert res["total_change_percent"] == Decimal("-50.00")
