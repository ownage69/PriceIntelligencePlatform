import logging

from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.api.deps import get_db_session
from app.core.exceptions import ProductAlreadyExistsError, ProductNotFoundError
from app.modules.prices.models import PriceHistory
from app.modules.products.models import Product
from app.models.catalog import Store, Tag
from app.modules.products.schemas import (
    BulkCreateResponse,
    PriceHistoryRead,
    ProductBulkCreate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductWithRelationsCreate
)
from app.schemas.pagination import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])

DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(get_db_session)]

class ProductCache:

    def __init__(self) -> None:
        self._cache: dict[tuple, PaginatedResponse[ProductRead]] = {}

    def get(self, key: tuple) -> PaginatedResponse[ProductRead] | None:
        return self._cache.get(key)

    def set(self, key: tuple, value: PaginatedResponse[ProductRead]) -> None:
        self._cache[key] = value

    def invalidate(self) -> None:
        self._cache.clear()

product_cache = ProductCache()


async def get_product_with_relations(
    session: AsyncSession,
    product_id: int,
) -> Product | None:
    return await session.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(
            joinedload(Product.store),
            selectinload(Product.tags),
        )
    )


async def get_active_products(
    session: AsyncSession,
    page: int = 1,
    size: int = 50,
    store_name: str | None = None,
    tag_name: str | None = None,
) -> tuple[int, list[Product]]:
    stmt = select(Product).where(Product.is_active.is_(True))
    count_stmt = select(func.count(Product.id.distinct())).where(Product.is_active.is_(True))

    if store_name:
        stmt = stmt.join(Product.store).where(Store.name.ilike(f"%{store_name}%"))
        count_stmt = count_stmt.join(Product.store).where(Store.name.ilike(f"%{store_name}%"))

    if tag_name:
        stmt = stmt.join(Product.tags).where(Tag.name.ilike(f"%{tag_name}%"))
        count_stmt = count_stmt.join(Product.tags).where(Tag.name.ilike(f"%{tag_name}%"))

    total_items = await session.scalar(count_stmt)

    offset = (page - 1) * size
    items = await session.scalars(
        stmt.options(
            joinedload(Product.store),
            selectinload(Product.tags)
        )
        .distinct()
        .order_by(Product.id)
        .offset(offset)
        .limit(size)
    )
    return total_items or 0, list(items)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    session: DatabaseSession,
) -> Product:
    target_url = str(product_in.target_url)

    product = Product(
        name=product_in.name,
        target_url=target_url,
        scrape_interval_minutes=product_in.scrape_interval_minutes,
    )
    session.add(product)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExistsError(target_url)

    result = await get_product_with_relations(session, product.id)
    product_cache.invalidate()
    return result


@router.post("/bulk", response_model=BulkCreateResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_products(
    data: ProductBulkCreate,
    session: DatabaseSession,
) -> BulkCreateResponse:
    products = [
        Product(name=str(target_url), target_url=str(target_url))
        for target_url in data.target_urls
    ]
    session.add_all(products)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExistsError("One or more URLs")
    product_cache.invalidate()
    return BulkCreateResponse(added_count=len(products))


@router.get("/", response_model=PaginatedResponse[ProductRead])
async def list_active_products(
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 50,
    store_name: Annotated[str | None, Query(description="Filter by store name")] = None,
    tag_name: Annotated[str | None, Query(description="Filter by tag name")] = None,
) -> PaginatedResponse[ProductRead]:
    cache_key = (page, size, store_name, tag_name)
    
    cached_result = product_cache.get(cache_key)
    if cached_result:
        return cached_result

    total_items, items = await get_active_products(
        session=session,
        page=page,
        size=size,
        store_name=store_name,
        tag_name=tag_name,
    )
    
    response = PaginatedResponse[ProductRead](
        total_items=total_items,
        page=page,
        size=size,
        total_pages=(total_items + size - 1) // size,
        items=[ProductRead.model_validate(item) for item in items],
    )
    
    product_cache.set(cache_key, response)
    return response


@router.get("/{product_id}/prices", response_model=list[PriceHistoryRead])
async def list_product_price_history(
    product_id: int,
    session: DatabaseSession,
) -> list[PriceHistory]:
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise ProductNotFoundError(product_id)

    result = await session.scalars(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(desc(PriceHistory.collected_at))
    )
    return list(result)


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    session: DatabaseSession,
) -> Product:
    product = await get_product_with_relations(session, product_id)
    if product is None:
        raise ProductNotFoundError(product_id)

    updates = product_in.model_dump(exclude_unset=True)
    tag_ids = updates.pop("tag_ids", None)

    if tag_ids is not None:
        tags = await session.scalars(select(Tag).where(Tag.id.in_(tag_ids)))
        product_tags = list(tags)
        if len(product_tags) != len(set(tag_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tags not found.",
            )
        product.tags = product_tags

    if "target_url" in updates:
        updates["target_url"] = str(updates["target_url"])

    for field, value in updates.items():
        setattr(product, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExistsError(str(updates.get("target_url", product.target_url)))

    result = await get_product_with_relations(session, product_id)
    product_cache.invalidate()
    return result


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    session: DatabaseSession,
) -> Response:
    product = await session.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError(product_id)

    await session.delete(product)
    await session.commit()
    product_cache.invalidate()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/with-relations", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product_with_relations(
    data: ProductWithRelationsCreate,
    session: DatabaseSession,
) -> Product:
    product = Product(
        name=data.name,
        target_url=str(data.target_url),
        store_id=data.store_id,
        scrape_interval_minutes=data.scrape_interval_minutes,
    )

    tags_list = []
    if data.tag_ids:
        tags = await session.scalars(select(Tag).where(Tag.id.in_(data.tag_ids)))
        tags_list = list(tags)
        if len(tags_list) != len(set(data.tag_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tags not found.",
            )
        product.tags = tags_list

    session.add(product)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExistsError(str(data.target_url))

    result = await get_product_with_relations(session, product.id)
    product_cache.invalidate()
    return result
