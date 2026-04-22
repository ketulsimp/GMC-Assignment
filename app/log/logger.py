import logging

logger = logging.Logger('logger')

format = logging.Formatter(fmt = "%(levelname)s %(asctime)s %(msg)s")
file_handler = logging.FileHandler(filename='logs.log')
file_handler.setFormatter(format)
logger.addHandler(file_handler)