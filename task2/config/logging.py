import logging

logging.basicConfig(filename="notification.log",level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("myapp")