from celery import Celery
from app.config.settings import settings

celery = Celery(
    "tasks",
    broker=settings.broker_uri,
    backend=settings.backend_uri
)
