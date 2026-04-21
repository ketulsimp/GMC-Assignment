from db.get_client import db
from schemas.auth import User, Google_Accounts, OAuthToken
from utils.logger import logger
from datetime import datetime

async def insert_user_to_db(user: User):
    
    logger.info('Inserting User into DB')
    res = await db.users.insert_one(user.model_dump())

    logger.info('Inserted User to DB successfully')
    
    print(res)

    return res.inserted_id


async def insert_google_acc_to_db(google_acc: Google_Accounts):

    logger.info('Inserted Google Acc to DB')


    res = await db.google_accs.insert_one(google_acc.model_dump())

    logger.info('Inserted Google Acc to DB successfully')


    print(res)

    return res 


async def insert_token_to_db(token: OAuthToken):
    
    logger.info('Inserting Token to DB')

    res = await db.tokens.insert_one(token.model_dump())

    logger.info('Inserted Token to DB successfully')

    print(res)

    return res 


async def update_access_token(refresh_token: str, access_token: str,expiry: datetime):
    
    logger.info('Updating Access Token to DB')


    res = await db.tokens.update_one({'refresh_token':refresh_token},{'$set':{'access_token':access_token,'expiry':expiry}})

    logger.info('Inserted Token to DB successfully')

    print(res)

    return res 




