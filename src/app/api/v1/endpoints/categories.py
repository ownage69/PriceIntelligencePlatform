from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError
from app.models.category import Category  
from app.modules.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(get_db_session)]


async def _get_category(session: AsyncSession, category_id: int) -> Category:
    category = await session.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise CategoryNotFoundError(category_id)
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, session: DatabaseSession) -> Category:
    category = Category(**data.model_dump())
    session.add(category)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CategoryAlreadyExistsError(data.name)

    await session.refresh(category)
    return category


@router.get("/", response_model=list[CategoryRead])
async def list_categories(session: DatabaseSession) -> list[Category]:
    categories = await session.scalars(select(Category).order_by(Category.id))
    return list(categories)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: DatabaseSession) -> Category:
    return await _get_category(session, category_id)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    session: DatabaseSession,
) -> Category:
    category = await _get_category(session, category_id)
    updates = data.model_dump(exclude_unset=True, exclude_none=True)
    name = updates.get("name", category.name)

    for field, value in updates.items():
        setattr(category, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CategoryAlreadyExistsError(name)

    await session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: DatabaseSession) -> Response:
    category = await _get_category(session, category_id)
    await session.delete(category)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
