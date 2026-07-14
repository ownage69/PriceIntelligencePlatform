from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

import app.db.models

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers


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

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
