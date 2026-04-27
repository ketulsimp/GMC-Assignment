import logging
from asgi_correlation_id import correlation_id_filter


logger = logging.getLogger(__name__)



console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log')

def configure_logging():
    cid_filter = correlation_id_filter(uuid_length=32)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('app.log')
    console_handler.addFilter(cid_filter())
    logging.basicConfig(
        handlers=[console_handler,file_handler],
        level=logging.INFO,
        format='%(levelname)s: \t %(asctime)s %(name)s:%(lineno)d [%(correlation_id)s] %(message)s'
    )

