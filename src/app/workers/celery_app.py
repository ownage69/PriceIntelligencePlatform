from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


celery_app = Celery(
    "price_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks.price_collection"],
)

celery_app.conf.update(
    accept_content=["json"],
    broker_connection_retry_on_startup=True,
    enable_utc=True,
    result_serializer="json",
    task_serializer="json",
    task_track_started=True,
    timezone="UTC",
)

celery_app.conf.beat_schedule = {
    "collect-due-prices-every-minute": {
        "task": "price_collection.collect_active_product_prices",
        "schedule": crontab(minute="*"),
    },
}
