from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

uri=settings.MONGO_URI

client=AsyncIOMotorClient(uri)
db=client['task-1']
users=db['users']
oauth_tokens=db['oauth_tokens']
merchant_accounts=db['merchant_accounts']