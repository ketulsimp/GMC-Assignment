import logging
from asgi_correlation_id import correlation_id_filter

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

cid_filter = correlation_id_filter(uuid_length=32)
console_handler = logging.StreamHandler()
console_handler.addFilter(cid_filter())

file_handler = logging.FileHandler("notification.log")
formatter = logging.Formatter('%(levelname)s : %(asctime)s - [%(correlation_id)s] - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
file_handler.addFilter(console_handler)

logger.addHandler(file_handler)
logger.addHandler(console_handler)