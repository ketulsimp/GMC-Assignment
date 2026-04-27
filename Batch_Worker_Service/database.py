from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

sync_client = MongoClient(os.getenv("MONGO_URL"))
sync_database = sync_client[os.getenv("DATABASE_NAME")]

products_collection_sync = sync_database["products"]