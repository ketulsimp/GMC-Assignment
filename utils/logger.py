
import logging
from fastapi import FastAPI


file_handler = logging.FileHandler("oauth.log")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[file_handler]
)

logger = logging.getLogger(__name__)

