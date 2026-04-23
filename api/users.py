from fastapi import APIRouter, Request, Cookie, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from utils.middleware import check_token_expiry
from typing import Annotated
from db.users import get_current_token, delete_token
from db.merchant_acc import add_accounts_to_db, get_merchant_account, set_selected_active_account
import httpx
import os
from schemas.merchant import MerchantAccount
from schemas.auth import User
from fastapi.exceptions import HTTPException
from utils.logger import logger

user = APIRouter(prefix='/api')

templates = Jinja2Templates(directory='templates')


async def fetch_google_merchant_accounts(request: Request,token: str):
    merchant=[]
    try:
        async with httpx.AsyncClient() as client:
            logger.info('Fetching Merchant accounts from Merchant API')
            res = await client.get('https://merchantapi.googleapis.com/accounts/v1/accounts/',
                            headers={
                                "Authorization":f"Bearer {token}"
                        }
                    )
            merchant = res.json()        
        

    except (httpx._exceptions.CloseError,httpx._exceptions.ConnectError, httpx._exceptions.ConnectTimeout) as e:
        logger.warning('Httpx connection error in fetching Merchants ',str(e))

        return templates.TemplateResponse(
           request=request, name='error.html',context={"msg":f"Httpx connection error in fetching Merchants {str(e)}"} 
        )
 
    return merchant      

@user.get('/me')
async def dashboard(request:Request,token: Annotated[str, Depends(check_token_expiry)]):
    try:
        if user:= request.session['user']:
            merchant = await fetch_google_merchant_accounts(request,token)
            if merchant.get('accounts') is None:
                 return templates.TemplateResponse(request=request, name='error.html',context={'msg':'No Merchant Acccounts For Google Account'})
                 
            res = await add_accounts_to_db(merchant, user.get('id'),User(email=user.get('email'),name=user.get('password'))) 
            print('Add Accs to DB Response : ',res)

            return templates.TemplateResponse(
                    request=request, name='dashboard.html',context={"user":user,"merchant":merchant,"selectedMerchant":res}
                )
        else:
            return templates.TemplateResponse(
                request=request,name='login.html'
            )
    

    except Exception as e:
        import traceback
        print("Unknown Error in dashboard page :", traceback.format_exc()) 
        logger.warning(str(e))
        return 


@user.post('/me')
async def get_merchant_acc(request: Request, token: Annotated[str, Depends(check_token_expiry)], merchant_id: Annotated[str, Form()]):
        merchant = await fetch_google_merchant_accounts(request, token)
        user = request.session['user']
        

        selectedMerchant = {}
        for account in merchant.get('accounts'):
            print('Account : ',account)
            if account.get('accountId') == merchant_id:
                 selectedMerchant=account
                 break
            
            
        res = await set_selected_active_account(user=User(name=user.get('name'),email=user.get('email')),userId=user.get('id'),selectedAccount=MerchantAccount(name=selectedMerchant.get('name'),accountId=selectedMerchant.get('accountId'),merchant_name=selectedMerchant.get('accountName')))
        
        logger.info(f'Set the Merchant {merchant_id} to user {user.get("name")}')

        
        return templates.TemplateResponse(
                    request=request, name='dashboard.html',context={"user":user,"merchant":merchant,"selectedMerchant":res}
        )


@user.get('/logout')
async def logout(request:Request,token: Annotated[str, Depends(check_token_expiry)]):
    try:
        userId = request.session['user'].get('id')
        
        async with httpx.AsyncClient() as client:
            response = await client.post("https://oauth2.googleapis.com/revoke",data={"token":token})
            print(response.json())

        res = await delete_token(userId)

        

        request.session.pop('google_acc_id')        
        request.session.pop('user')
        return RedirectResponse('/api/auth/login')

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc()) 
        logger.warning(str(e))
        return {"error": str(e)}





