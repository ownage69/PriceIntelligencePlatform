from fastapi import FastAPI, status

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Platform for monitoring and analysing marketplace prices.",
)


@app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}

