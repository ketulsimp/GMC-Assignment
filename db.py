from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv() 


client = AsyncIOMotorClient(os.getenv("MONGO_URL")) 
db = client[os.getenv("DATABASE_NAME")]


products_collection = db["products"]

async def create_db_indexes():
    await products_collection.create_index(
        [("sku", pymongo.ASCENDING)],
        unique=True
    )

    await products_collection.create_index(
        [("product_id", pymongo.ASCENDING)],
        unique=True
    )