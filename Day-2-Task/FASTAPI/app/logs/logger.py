from pythonjsonlogger import jsonlogger
from asgi_correlation_id import CorrelationIdFilter
import logging

cid_filter = CorrelationIdFilter(uuid_length=32)
web_logger = logging.Logger("logger")
worker_logger = logging.Logger("logger")
file_handler_web = logging.FileHandler(filename='app/logs/web_logs.log')
stream_handler_web = logging.StreamHandler()
fmt_web = jsonlogger.JsonFormatter(
    "%(levelname)s %(asctime)s %(funcName)s %(message)s [%(correlation_id)s]",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
)
stream_fmt_web = logging.Formatter(
    fmt="%(levelname)s %(asctime)s %(funcName)s %(message)s [%(correlation_id)s]",
)

file_handler_web.setFormatter(fmt_web)
file_handler_web.addFilter(cid_filter)
stream_handler_web.setFormatter(stream_fmt_web)
stream_handler_web.addFilter(cid_filter)
web_logger.addHandler(file_handler_web)
web_logger.addHandler(stream_handler_web)


def logger_decorator(func):
    def wrapper(*args,**kwargs):
        web_logger.info('Request Started.')
        response = func(args,kwargs)
        web_logger.info('Request Completed.')
        return response
    return logger_decorator