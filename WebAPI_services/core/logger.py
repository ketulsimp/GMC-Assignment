


import logging
import json
from datetime import datetime

SERVICE_NAME = "web-api-service"


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": SERVICE_NAME,
            "level": record.levelname,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
        }
        line = json.dumps(log)
        # if record.levelname == "INFO":
        #     return f"\033[91m{line}\033[0m"
        return line


def get_logger(name="app_logger"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = JSONFormatter()

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        file_handler = logging.FileHandler("web-api.log")
        file_handler.setFormatter(formatter)

        logger.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
    return logger