from typing import Generic, List, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total_items: int
    page: int
    size: int
    total_pages: int
    items: List[T]
