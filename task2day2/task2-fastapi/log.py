import logging
from pythonjsonlogger import jsonlogger


logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename='app.log')
handler.setFormatter(jsonlogger.JsonFormatter(
     "%(asctime)s %(levelname)s [%(correlation_id)s] %(message)s"
))

logger.addHandler(handler)
logger.setLevel(logging.INFO)