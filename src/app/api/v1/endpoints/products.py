from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.exceptions import ProductAlreadyExistsError, ProductNotFoundError
from app.modules.prices.models import PriceHistory
from app.modules.products.models import Product
from app.modules.products.schemas import PriceHistoryRead, ProductCreate, ProductRead

router = APIRouter(prefix="/products", tags=["products"])

DatabaseSession: TypeAlias = Annotated[AsyncSession, Depends(get_db_session)]


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


@router.get("/", response_model=list[ProductRead])
async def list_active_products(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Product]:
    result = await session.scalars(
        select(Product)
        .where(Product.is_active.is_(True))
        .order_by(Product.id)
        .offset(offset)
        .limit(limit)
    )
    return list(result)


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
