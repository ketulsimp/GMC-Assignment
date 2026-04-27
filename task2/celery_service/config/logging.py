import logging
from asgi_correlation_id import correlation_id_filter

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("notification.log")
formatter = logging.Formatter('%(levelname)s : %(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
