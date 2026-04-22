from fastapi import APIRouter, Request, HTTPException, Depends
from google.shopping.merchant_accounts_v1 import AccountsServiceAsyncClient
from google.shopping.merchant_accounts_v1 import ListAccountsRequest
from app.utilities.merchant_utils import get_credentials, decode_account, store_merchant_details, update_current_merchant
from app.error.exceptions import TokenNotFoundError
from app.log.logger import logger
from app.utilities.auth_utils import authenticate

merchants_rt = APIRouter(prefix='/merchants', dependencies=[Depends(authenticate)])

@merchants_rt.get('/')
async def get_all_accounts(request: Request):
    user_id = request.session.get('user')
    try:
        credentials = await get_credentials(user_id)
    except TokenNotFoundError:
        logger.exception(f"Token error for user {user_id}")
        raise HTTPException(status_code=500,detail='Token Error')
    client = AccountsServiceAsyncClient(credentials=credentials)
    req = ListAccountsRequest()
    response = await client.list_accounts(request=req)
    accounts = [decode_account(account) async for account in response]
    if accounts:
        await store_merchant_details(user_id,accounts)
        return accounts
    return "No Merchants Account Found. Please Create atleast one Merchant Account First to proceed."

@merchants_rt.get('/select-merchant')
async def select_merchant(request: Request, merchant_id: str):
    user_id = request.session.get('user')
    await update_current_merchant(user_id,merchant_id)