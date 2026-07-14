from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        request.state.db_session = session
        try:
            yield session
        finally:
            request.state.db_session = None
