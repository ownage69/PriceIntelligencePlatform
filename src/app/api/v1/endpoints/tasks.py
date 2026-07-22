from typing import Annotated

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.modules.products.models import Product
from app.workers.celery_app import celery_app
from app.workers.tasks.price_collection import collect_product_price

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStartResponse(BaseModel):
    task_id: str
    product_name: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    message: str | None = None


@router.post("/collect/{product_id}", response_model=TaskStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_single_collection(
    product_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> TaskStartResponse:
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    task = collect_product_price.delay(product_id)
    return TaskStartResponse(task_id=task.id, product_name=product.name)


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    task = AsyncResult(task_id, app=celery_app)
    
    message = None
    if isinstance(task.info, dict):
        message = task.info.get("message")
    elif isinstance(task.info, Exception):
        message = str(task.info)
        
    return TaskStatusResponse(task_id=task_id, status=task.status, message=message)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_task(task_id: str) -> Response:
    celery_app.control.revoke(task_id, terminate=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
