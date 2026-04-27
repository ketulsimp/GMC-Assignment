import logging

logger = logging.getLogger(__name__)


console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('celery_app.log')

logger.addHandler(console_handler)
logger.addHandler(file_handler)


logger.setLevel(level='INFO')
