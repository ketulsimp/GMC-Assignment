from db.get_client import db
from db.users import get_selected_active_account, set_selected_active_account
from utils.logger import logger
from pymongo import ReturnDocument
from schemas.merchant import MerchantAccount
from schemas.auth import User

async def add_accounts_to_db(merchants: list, userId: str,user: User):
    logger.info('Inserting Merchant Accounts into DB')

    res = await get_selected_active_account(userId=userId)
    
    if res is None:


        account = merchants.get('accounts')[0]
        res = await set_selected_active_account(user=user,userId=userId,selectedAccount=MerchantAccount(name=account.get('name'),accountId=account.get('accountId'),merchant_name=account.get('accountName')))
        return res
    else:
        print(res)
        return res


async def get_merchant_account(merchantId: str):
    logger.info('Getting Merchant Account Info')
    res = await db.merchant_accounts.find_one({'accounts.$.accountId':merchantId},{"accounts.$":1})

    return res 
