from pymongo import AsyncMongoClient, MongoClient
from app.config.settings import settings
from app.logs.logger import logger

class AsyncDbManager():
    client: AsyncMongoClient = None
    db = None

class DbManager():
    client: MongoClient = None
    db = None
    
async_manager = AsyncDbManager()
manager = DbManager()

async def connect_to_mongo():
    async_manager.client = AsyncMongoClient(settings.mongo_uri,serverSelectionTimeoutMS=5000)
    manager.client = MongoClient(settings.mongo_uri,serverSelectionTimeoutMS=5000)
    try:
        await async_manager.client.admin.command('ping')
        manager.client.admin.command('ping')
        async_manager.db = async_manager.client["task_2"]
        manager.db = manager.client["task_2"]
        logger.info('DB Connection Successful')
    except Exception as e:
        logger.exception("Database Connection Unsuccessful.")
        
        
async def disconnect_to_mongo():
    await async_manager.client.aclose()
    manager.client.close()
    
async def get_db():
    return async_manager.db

def get_sync_db():
    return manager.db