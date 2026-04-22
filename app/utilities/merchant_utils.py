from google.oauth2.credentials import Credentials
from app.config.db import get_mongo_db
from app.error.exceptions import TokenNotFoundError, UserNotFoundError
from google.shopping.merchant_accounts_v1.types.accounts import Account
from bson.objectid import ObjectId
from app.utilities.auth_utils import get_token

async def get_credentials(user_id):
    token = await get_token(user_id)
    return Credentials(
        token=token
    )
    
def decode_account(account: Account):
    return {
        'account_id': account.account_id,
        'account_name': account.account_name
    }
    
async def store_merchant_details(user_id: str,merchants: list):
    db = get_mongo_db()
    user_details = await db.users.find_one({'_id':ObjectId(user_id)})
    merchant_1 = merchants[0].get('account_id')
    if user_details is None:
        raise UserNotFoundError
    await db.merchant_accounts.update_one({'user_id':user_id,'google_account':user_details.get('email')},{'$set': {'merchants':merchants, 'selected_merchant_id':merchant_1}},upsert=True)

async def update_current_merchant(user_id: str, merchant_id: str):
    db = get_mongo_db()
    await db.merchant_accounts.update_one({'user_id': user_id},{'$set': {'selected_merchant_id': merchant_id}},)
    
    