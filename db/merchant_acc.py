from db.get_client import db
from db.users import get_selected_active_account, set_selected_active_account
from utils.logger import logger
from pymongo import ReturnDocument

async def add_accounts_to_db(merchants: list, userId: str,google_id: str):

    logger.info('Inserting User into DB')

    res = await db.merchant_accounts.find_one_and_update(
            {"user_id":userId,"google_id":google_id},
            {"$set":
                {"merchant_accs":merchants}

            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    res = await get_selected_active_account(userId=userId)

    if res is None:
        res = await set_selected_active_account(userId=userId,selectedAccountId=merchants.get('accounts')[0].get("accountId"))
        return res.get('selected_active_account')
    else:
        print(res.get('selected_active_account'))
        return res.get('selected_active_account')



async def get_merchant_account(merchantId: str):

    logger.info('Getting Merchant Account Info')


    res = await db.merchant_accounts.find_one({'accounts.$.accountId':merchantId},{"accounts.$":1})

    return res 



    

