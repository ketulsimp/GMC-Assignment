import logging
from pythonjsonlogger import jsonlogger


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler("app.log")
    handler.setFormatter(jsonlogger.JsonFormatter(
     "%(asctime)s %(levelname)s [%(correlation_id)s] %(message)s"
    ))
    
    logger.addHandler(handler)

    return logger