import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

import app.db.models

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
logger.info("Starting Price Intelligence Platform...")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Platform for monitoring and analysing marketplace prices.",
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def action_logging_middleware(request: Request, call_next):
    path = request.url.path
    
    if path.startswith("/docs") or path.startswith("/openapi.json"):
        return await call_next(request)

    method = request.method
    action_name = "UNKNOWN"
    if method == "POST":
        action_name = "CREATE"
    elif method == "GET":
        action_name = "READ"
    elif method in ("PUT", "PATCH"):
        action_name = "UPDATE"
    elif method == "DELETE":
        action_name = "DELETE"

    logger.info(f"Action started: [{action_name}] on {path}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"Action completed: [{action_name}] on {path} | Status: {response.status_code} | Time: {process_time:.3f}s")
    
    return response

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
