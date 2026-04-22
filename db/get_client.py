from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()


client = AsyncMongoClient(os.environ['MONGO_URL'])
db = client['merchant']