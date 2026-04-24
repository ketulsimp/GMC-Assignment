import  logging

logger = logging.getLogger(__name__)



console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log')


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [console_handler, file_handler]
)

