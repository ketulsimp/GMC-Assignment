
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))
db = client["oauth_db_final"]

db.users.create_index([("email", ASCENDING)], unique=True)
db.oauth_tokens.create_index([("user_id", ASCENDING)], unique=True)


class TokenRevokedError(Exception):
    pass
