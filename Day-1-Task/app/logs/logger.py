from pythonjsonlogger import jsonlogger
from asgi_correlation_id import CorrelationIdFilter
import logging

cid_filter = CorrelationIdFilter(uuid_length=32)
web_logger = logging.Logger("logger")
worker_logger = logging.Logger("logger")
file_handler_web = logging.FileHandler(filename='app/logs/web_logs.log')
file_handler_celery = logging.FileHandler(filename='app/logs/celery_logs.log')
stream_handler_web = logging.StreamHandler()
stream_handler_celery = logging.StreamHandler()
fmt_web = jsonlogger.JsonFormatter(
    "%(levelname)s %(asctime)s %(funcName)s %(message)s [%(correlation_id)s]",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
)
stream_fmt_web = logging.Formatter(
    fmt="%(levelname)s %(asctime)s %(funcName)s %(message)s [%(correlation_id)s]",
)
fmt_celery = jsonlogger.JsonFormatter(
    "%(levelname)s %(asctime)s %(funcName)s %(message)s",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
)
stream_fmt_celery = logging.Formatter(
    fmt="%(levelname)s %(asctime)s %(funcName)s %(message)s",
)
file_handler_web.setFormatter(fmt_web)
file_handler_web.addFilter(cid_filter)
stream_handler_web.setFormatter(stream_fmt_web)
stream_handler_web.addFilter(cid_filter)
web_logger.addHandler(file_handler_web)
web_logger.addHandler(stream_handler_web)


file_handler_celery.setFormatter(fmt_celery)
stream_handler_celery.setFormatter(stream_fmt_celery)
worker_logger.addHandler(file_handler_celery)
worker_logger.addHandler(stream_handler_celery)

