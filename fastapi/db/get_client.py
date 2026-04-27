from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ['MONGO_URL'])
db = client['simprosys-api']