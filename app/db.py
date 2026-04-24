from pymongo import MongoClient
import os
MONGO_URI = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URI)

db = client.task2
collection = db.products
