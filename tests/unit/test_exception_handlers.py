import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BaseAPIException,
    ProductAlreadyExistsError,
    ProductNotFoundError,
    StoreAlreadyExistsError,
    StoreNotFoundError,
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    register_exception_handlers,
    _rollback_request_session
)

def test_custom_exceptions_init():
    assert ProductAlreadyExistsError("url").status_code == 409
    assert ProductNotFoundError(1).status_code == 404
    assert StoreAlreadyExistsError("domain").status_code == 409
    assert StoreNotFoundError(1).status_code == 404
    assert CategoryAlreadyExistsError("cat").status_code == 409
    assert CategoryNotFoundError(1).status_code == 404
    assert BaseAPIException("msg", {"a": 1}).status_code == 400

def test_exception_handlers_integration():
    app = FastAPI()
    register_exception_handlers(app)
    
    @app.get("/base")
    async def raise_base():
        raise ProductNotFoundError(42)
        
    @app.get("/sqlalchemy")
    async def raise_sa(request: Request):
        request.state.db_session = AsyncMock()
        raise SQLAlchemyError("db error")

    @app.get("/unhandled")
    async def raise_unhandled():
        raise ValueError("unexpected")

    class Dummy(BaseModel):
        val: int

    @app.post("/validation")
    async def raise_validation(dummy: Dummy):
        return dummy

    client = TestClient(app, raise_server_exceptions=False)
    
    res_base = client.get("/base")
    assert res_base.status_code == 404
    assert res_base.json()["error"]["type"] == "ProductNotFoundError"
    
    res_sa = client.get("/sqlalchemy")
    assert res_sa.status_code == 500
    assert res_sa.json()["error"]["type"] == "SQLAlchemyError"
    
    res_unhandled = client.get("/unhandled")
    assert res_unhandled.status_code == 500
    assert res_unhandled.json()["error"]["type"] == "InternalServerError"
    
    res_val = client.post("/validation", json={"val": "not-int"})
    assert res_val.status_code == 422
    assert res_val.json()["error"]["type"] == "RequestValidationError"

class FakeAsyncSession(AsyncSession):
    def __init__(self):
        self.rollback = AsyncMock()

@pytest.mark.asyncio
async def test_rollback_request_session_logic():
    mock_request = MagicMock(spec=Request)
    fake_session = FakeAsyncSession()
    mock_request.state.db_session = fake_session
    
    await _rollback_request_session(mock_request)
    fake_session.rollback.assert_called_once()
    
    mock_request_no_session = MagicMock(spec=Request)
    mock_request_no_session.state.db_session = None
    await _rollback_request_session(mock_request_no_session)
