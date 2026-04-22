from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from utils.middleware import check_token_expiry
from typing import Annotated
from db.users import get_current_token, delete_token
from db.merchant_acc import add_accounts_to_db, get_merchant_account

import httpx

import os
from utils.logger import logger

user = APIRouter(prefix='/api')

templates = Jinja2Templates(directory='templates')

@user.get('/me')
async def dashboard(request:Request,token: Annotated[str, Depends(check_token_expiry)]):
    try:
        if request.method == "POST":
            selectedId = request.form['merchant_id']
            user = request.session['user']
            res = await get_merchant_account(selectedId)
            return templates.TemplateResponse(
                    request=request, name='dashboard.html',context={"user":user,"merchant":merchant,"selectedMerchantId":selectedId,"selectedMerchantAccount":res}
                )

        if user:= request.session['user']:
            merchant=[]
            async with httpx.AsyncClient() as client:
                res = await client.get('https://merchantapi.googleapis.com/accounts/v1/accounts/',
                        headers={
                             "Authorization":f"Bearer {token}"
                        }
                    )
                print(res)
                merchant = res.json()        
                print(merchant)                

            google_id = request.session['google_acc_id']

            res = await add_accounts_to_db(merchant, user.get('id'),google_id) 



            return templates.TemplateResponse(
                    request=request, name='dashboard.html',context={"user":user,"merchant":merchant,"selectedMerchantId":res}
                )
        else:
            return templates.TemplateResponse(
                request=request,name='login.html'
            )

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc()) 
        logger.warning(str(e))
        request.session['state']
        return {"error": str(e)}






@user.get('/logout')
async def logout(request:Request):
    try:
        userId = request.session['id']
        res = await delete_token(userId)
        async with httpx.AsyncClient() as client:
                res = await client.get('https://merchantapi.googleapis.com/accounts/v1/accounts/',
                        headers={
                             "Authorization":f"Bearer {token}"
                        }
                    )
                print(res)
                res = res.json()
                print(res)
                merchants = res.json()  

        request.session.pop('user')
        return RedirectResponse('/api/auth/login')

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc()) 
        logger.warning(str(e))
        return {"error": str(e)}




