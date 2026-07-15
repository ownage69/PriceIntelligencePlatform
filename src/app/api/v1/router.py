from fastapi import APIRouter

from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.stores import router as stores_router
from app.api.v1.endpoints.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(products_router)
api_router.include_router(stores_router)
api_router.include_router(tasks_router)
