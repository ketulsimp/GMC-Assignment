from pythonjsonlogger import jsonlogger
from asgi_correlation_id import CorrelationIdFilter
import logging

cid_filter = CorrelationIdFilter(uuid_length=32)
logger = logging.Logger("logger")
file_handler = logging.FileHandler(filename='app/logs/logs.log')
stream_handler = logging.StreamHandler()
fmt = jsonlogger.JsonFormatter(
    "%(asctime)s %(funcName)s %(levelname)s %(message)s [%(correlation_id)s]",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
)
stream_fmt = logging.Formatter(
    fmt="%(asctime)s %(funcName)s %(levelname)s %(message)s [%(correlation_id)s]",
)
file_handler.setFormatter(fmt)
file_handler.addFilter(cid_filter)
stream_handler.setFormatter(stream_fmt)
stream_handler.addFilter(cid_filter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

