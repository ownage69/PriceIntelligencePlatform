import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request

from app.api.deps import get_db_session

@pytest.mark.asyncio
async def test_get_db_session():
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    
    with patch("app.api.deps.async_session_factory") as mock_factory:
        mock_session = AsyncMock()
        mock_factory.return_value.__aenter__.return_value = mock_session
        
        gen = get_db_session(mock_request)
        
        session = await anext(gen)
        
        assert session == mock_session
        assert mock_request.state.db_session == mock_session
        
        try:
            await anext(gen)
        except StopAsyncIteration:
            pass
            
        assert mock_request.state.db_session is None
