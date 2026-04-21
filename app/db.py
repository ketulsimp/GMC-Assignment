"""
Database Connection Module
Contains asyncronous functions for connecting and disconnecting to mongo during the entire session of fastapi app
Also has the function which returns the db instance
"""

from pymongo import AsyncMongoClient
from app.settings import settings
from app.logger import logger

_client: AsyncMongoClient = None
_db = None

async def connect_to_mongo():
    global _client,_db
    _client = AsyncMongoClient(settings.mongo_uri,serverSelectionTimeoutMS=5000)
    _db = _client["day_1_task"]
    try:
        await _client.admin.command('ping')
        logger.info("MongoDb Connection successful.")
    except Exception:
        logger.error("Connection to MongoDb Unsuccessfull.")
        
async def disconnect_to_mongo():
    await _client.aclose()
    
def get_mongo_db():
    return _db