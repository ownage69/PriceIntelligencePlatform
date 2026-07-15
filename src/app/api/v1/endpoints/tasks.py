from celery.result import AsyncResult
from fastapi import APIRouter, status
from pydantic import BaseModel

from app.workers.celery_app import celery_app
from app.workers.tasks.price_collection import collect_active_product_prices

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStartResponse(BaseModel):

    task_id: str


class TaskStatusResponse(BaseModel):

    task_id: str
    status: str


@router.post("/collect", response_model=TaskStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_price_collection() -> TaskStartResponse:
    task = collect_active_product_prices.delay()
    return TaskStartResponse(task_id=task.id)


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    task = AsyncResult(task_id, app=celery_app)
    return TaskStatusResponse(task_id=task_id, status=task.status)
