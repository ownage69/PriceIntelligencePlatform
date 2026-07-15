from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.exceptions import StoreAlreadyExistsError, StoreNotFoundError
from app.models.catalog import Store
from app.modules.stores.schemas import StoreCreate, StoreRead, StoreUpdate

router = APIRouter(prefix="/stores", tags=["stores"])

DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(get_db_session)]


async def _get_store(session: AsyncSession, store_id: int) -> Store:
    store = await session.scalar(select(Store).where(Store.id == store_id))
    if store is None:
        raise StoreNotFoundError(store_id)
    return store


@router.post("/", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
async def create_store(data: StoreCreate, session: DatabaseSession) -> Store:
    store = Store(**data.model_dump())
    session.add(store)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise StoreAlreadyExistsError(data.domain)

    await session.refresh(store)
    return store


@router.get("/", response_model=list[StoreRead])
async def list_stores(session: DatabaseSession) -> list[Store]:
    stores = await session.scalars(select(Store).order_by(Store.id))
    return list(stores)


@router.get("/{store_id}", response_model=StoreRead)
async def get_store(store_id: int, session: DatabaseSession) -> Store:
    return await _get_store(session, store_id)


@router.put("/{store_id}", response_model=StoreRead)
async def update_store(
    store_id: int,
    data: StoreUpdate,
    session: DatabaseSession,
) -> Store:
    store = await _get_store(session, store_id)
    updates = data.model_dump(exclude_unset=True, exclude_none=True)
    domain = updates.get("domain", store.domain)

    for field, value in updates.items():
        setattr(store, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise StoreAlreadyExistsError(domain)

    await session.refresh(store)
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(store_id: int, session: DatabaseSession) -> Response:
    store = await _get_store(session, store_id)
    await session.delete(store)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
