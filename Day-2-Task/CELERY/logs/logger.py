from pythonjsonlogger import jsonlogger
import logging
from celery.utils.log import get_task_logger


celery_logger = get_task_logger("celery_logger")

worker_logger = logging.Logger("logger")

file_handler_celery = logging.FileHandler(filename='logs/celery_logs.log')

stream_handler_celery = logging.StreamHandler()

fmt_celery = jsonlogger.JsonFormatter(
    "%(levelname)s %(asctime)s %(funcName)s %(message)s",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
)
stream_fmt_celery = logging.Formatter(
    fmt="%(levelname)s %(asctime)s %(funcName)s %(message)s",
)


file_handler_celery.setFormatter(fmt_celery)
stream_handler_celery.setFormatter(stream_fmt_celery)
worker_logger.addHandler(file_handler_celery)
worker_logger.addHandler(stream_handler_celery)

