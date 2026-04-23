from fastapi import APIRouter, Request, HTTPException, Depends
from google.shopping.merchant_accounts_v1 import AccountsServiceAsyncClient
from google.shopping.merchant_accounts_v1 import ListAccountsRequest
from app.utilities.merchant_utils import get_credentials, decode_account, store_merchant_details, update_current_merchant
from app.error.exceptions import TokenNotFoundError
from app.log.logger import logger
from app.utilities.auth_utils import authenticate
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

merchants_rt = APIRouter(prefix='/merchants', dependencies=[Depends(authenticate)])
templates = Jinja2Templates(directory='app/templates')

@merchants_rt.get('/',response_class=HTMLResponse)
async def get_all_accounts(request: Request):
    """
    Fetches the merchant account assosciated with the access token google account and displays them to the user.
    Gracefully handled edge cases of no accounts assosciated with the user or updation of the merchant_accounts collection
    selected_merchant_id field.
    """
    
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
    context = {'accounts': accounts}
    if accounts:
        merchant_id = await store_merchant_details(user_id,accounts)
        context['selected_merchant'] = merchant_id
        request.session['current_merchant'] = merchant_id
    return templates.TemplateResponse(
        request=request,
        name='merchant.html',
        context=context
    )
    
@merchants_rt.get('/select-merchant')
async def select_merchant(request: Request, merchant_id: int):
    """
    Selects the merchant_id and subsequently changes the merchant id in the database.
    Key Considerations:
        The selected merchant_id needs to be present the available merchant_id in the database which depends on 
        the dynamically fetched merchant list so there is no possibiliy of mismatch or the selected merchant_id not existing
        error.
    """
    
    user_id = request.session.get('user')
    await update_current_merchant(user_id,merchant_id)
    request.session['current_merchant'] = merchant_id
    return RedirectResponse(url=request.url_for('get_all_accounts'))