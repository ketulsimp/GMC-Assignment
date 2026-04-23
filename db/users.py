from db.get_client import db
from schemas.auth import User, Google_Accounts, OAuthToken
from schemas.merchant import MerchantAccount
from utils.logger import logger
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument

async def insert_user_to_db(user: User):
    
    logger.info('Inserting User into DB')

    user = user.model_dump()
    res = await db.users.find_one_and_update({'email':user.get('email')},
        {"$set":{
            "name":user.get('name'),
            "password":user.get('password')
        }},        
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    logger.info('Inserted User to DB successfully')
    

    return res.get('_id')


async def insert_google_acc_to_db(google_acc: Google_Accounts):

    logger.info('Inserted Google Acc to DB')
    google_acc = google_acc.model_dump()

    res = await db.google_accs.find_one_and_update({'email':google_acc.get('email')},
                                                   {
                                                       "$set":{
                                                           "email":google_acc.get('email'),
                                                           "name":google_acc.get('name'),
                                                           "picture":google_acc.get('picture')
                                                       }
                                                   },
                                                    upsert=True,
                                                    return_document=ReturnDocument.AFTER
                                                   )

    logger.info('Inserted Google Acc to DB successfully')



    return res.get('_id')


async def insert_token_to_db(token: OAuthToken):
    
    logger.info('Inserting Token to DB')
    token = token.model_dump()
    res = await db.tokens.find_one_and_update({'user_id':token.get('user_id')},
                                              {
                                                  '$set':{
                                                        "access_token":token.get('access_token'),
                                                        "refresh_token":token.get('refresh_token'),
                                                        "expiry":token.get('expiry')
                                                    }
                                              },
                                              upsert=True,
                                              return_document=ReturnDocument.AFTER
                                                )

    logger.info('Inserted Token to DB successfully')
    return res 




async def update_access_token(refresh_token: str, access_token: str,expiry: datetime):
    logger.info('Updating Access Token to DB')
    res = await db.tokens.update_one({'refresh_token':refresh_token},{'$set':{'access_token':access_token,'expiry':expiry}})
    logger.info('Inserted Token to DB successfully')
    return res 


async def get_current_token(userId: str):
    logger.info('Getting Current Token from DB')
    res = await db.tokens.find_one({'user_id':userId})
    logger.info('Inserted Token to DB successfully')
    return res 

async def delete_token(userId: str): 
    logger.info('Deleting Revoked Token from DB')
    res = await db.tokens.find_one_and_update({'user_id':userId},{'$set':{}},return_document=ReturnDocument.AFTER)
    logger.info('Deleted Token from  DB successfully')
    return res.get('access_token')


async def get_selected_active_account(userId: str):
    res = await db.users.find_one({'_id':ObjectId(userId)},{"_id":0,"selected_active_account":1})

    return res.get('selected_active_account') if res else None


async def set_selected_active_account(user: User, userId: str,selectedAccount: MerchantAccount):

    res = await db.users.find_one_and_update({'_id':ObjectId(userId)},{"$set":{"selected_active_account":selectedAccount.model_dump(),"name":user.name,"email":user.email,"password":user.password  }},upsert=True,return_document=ReturnDocument.AFTER)


    return res.get('selected_active_account',{})




