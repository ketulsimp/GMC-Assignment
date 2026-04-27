from celery import Celery
from conf.settings import settings
from celery.signals import after_setup_task_logger
from celery.app.log import TaskFormatter

celery = Celery(
    "tasks",
    broker=settings.broker_uri,
    backend=settings.backend_uri
)

celery.conf.task_routes = {
    'tasks.batch_store_in_mongo': {'queue':'new-queue'}
}


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(TaskFormatter('%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s]'))