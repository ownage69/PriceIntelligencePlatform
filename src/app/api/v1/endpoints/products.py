from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.api.deps import get_db_session
from app.core.exceptions import ProductAlreadyExistsError, ProductNotFoundError
from app.modules.prices.models import PriceHistory
from app.modules.products.models import Product
from app.models.catalog import Tag
from app.modules.products.schemas import (
    BulkCreateResponse,
    PriceHistoryRead,
    ProductBulkCreate,
    ProductCreate,
    ProductRead,
    ProductWithRelationsCreate
)
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/products", tags=["products"])

DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(get_db_session)]


async def get_active_products(
    session: AsyncSession,
    page: int = 1,
    size: int = 50,
) -> tuple[int, list[Product]]:
    offset = (page - 1) * size
    total_items = await session.scalar(
        select(func.count()).select_from(Product).where(Product.is_active.is_(True))
    )
    items = await session.scalars(
        select(Product)
        .where(Product.is_active.is_(True))
        .options(
            joinedload(Product.store), 
            selectinload(Product.tags)  
        )
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

    product = Product(name=product_in.name, target_url=target_url)
    session.add(product)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExistsError(target_url)

    await session.refresh(product)
    return product


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
        raise ProductAlreadyExistsError("Один или несколько URL")
    return BulkCreateResponse(added_count=len(products))


@router.get("/", response_model=PaginatedResponse[ProductRead])
async def list_active_products(
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> PaginatedResponse[ProductRead]:
    total_items, items = await get_active_products(
        session=session,
        page=page,
        size=size,
    )
    return PaginatedResponse[ProductRead](
        total_items=total_items,
        page=page,
        size=size,
        total_pages=(total_items + size - 1) // size,
        items=[ProductRead.model_validate(item) for item in items],
    )


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

@router.post("/with-relations", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product_with_relations(
    data: ProductWithRelationsCreate,
    session: DatabaseSession,
) -> Product:
    product = Product(
        name=data.name,
        target_url=str(data.target_url),
        store_id=data.store_id
    )
    session.add(product)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise ProductAlreadyExistsError(str(data.target_url))

    if data.tag_ids:
        tags = await session.scalars(select(Tag).where(Tag.id.in_(data.tag_ids)))
        tags_list = list(tags)

        if len(tags_list) != len(data.tag_ids):
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tags not found. Transaction fully rolled back."
            )
        
        product.tags = tags_list

    await session.commit()
    
    result = await session.scalar(
        select(Product)
        .where(Product.id == product.id)
        .options(joinedload(Product.store), selectinload(Product.tags))
    )
    return result
