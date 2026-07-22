from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, details: Any | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class ProductAlreadyExistsError(BaseAPIException):

    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, target_url: str) -> None:
        super().__init__(
            message="A product with this target URL already exists.",
            details={"target_url": target_url},
        )


class ProductNotFoundError(BaseAPIException):

    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, product_id: int) -> None:
        super().__init__(
            message="Product not found.",
            details={"product_id": product_id},
        )


class StoreAlreadyExistsError(BaseAPIException):

    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, domain: str) -> None:
        super().__init__(
            message="A store with this domain already exists.",
            details={"domain": domain},
        )


class StoreNotFoundError(BaseAPIException):

    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, store_id: int) -> None:
        super().__init__(
            message="Store not found.",
            details={"store_id": store_id},
        )


class ErrorBody(BaseModel):

    model_config = ConfigDict(extra="forbid")

    type: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):

    model_config = ConfigDict(extra="forbid")

    success: Literal[False] = False
    error: ErrorBody

class CategoryAlreadyExistsError(BaseAPIException):
    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self, name: str) -> None:
        super().__init__(
            message="A category with this name already exists.",
            details={"name": name},
        )


class CategoryNotFoundError(BaseAPIException):
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self, category_id: int) -> None:
        super().__init__(
            message="Category not found.",
            details={"category_id": category_id},
        )

def _error_response(
    *,
    status_code: int,
    error_type: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorBody(type=error_type, message=message, details=details)
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


def _validation_details(error: RequestValidationError) -> list[dict[str, str]]:
    return [
        {
            "field": ".".join(str(location) for location in item["loc"]),
            "message": item["msg"],
            "type": item["type"],
        }
        for item in error.errors()
    ]


async def _rollback_request_session(request: Request) -> None:
    session = getattr(request.state, "db_session", None)
    if isinstance(session, AsyncSession):
        await session.rollback()


async def base_api_exception_handler(
    request: Request,
    exception: BaseAPIException,
) -> JSONResponse:
    return _error_response(
        status_code=exception.status_code,
        error_type=type(exception).__name__,
        message=exception.message,
        details=exception.details,
    )


async def request_validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_type=type(exception).__name__,
        message="Request validation failed.",
        details=_validation_details(exception),
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exception: SQLAlchemyError,
) -> JSONResponse:
    await _rollback_request_session(request)
    logger.exception("Database request failed: %s", exception)
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type=type(exception).__name__,
        message="A database error occurred.",
    )


async def unhandled_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    logger.exception("Unhandled request error: %s", exception)
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="InternalServerError",
        message="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

