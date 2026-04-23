from fastapi import FastAPI,Request,Form
from routers.auth import router
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from database.db import merchant_accounts,oauth_tokens
from fastapi.templating import Jinja2Templates
from utils.jwt import verify_user
from datetime import datetime
from utils.refresh import refresh_access_token
import httpx

load_dotenv()

app=FastAPI()

app.include_router(router)
templates=Jinja2Templates(directory='templates')

@app.get('/welcome')
async def welcome_google(request: Request):
    token = request.cookies.get('token')
    if not token:
        return RedirectResponse('/login')

    user=await verify_user(token)
    email=user.get('email')
    name=user.get('name')

    query=await oauth_tokens.find_one({'email': email})
    if not query:
        return RedirectResponse('/login')

    access_token = query['access_token']
    if datetime.now() > query['expiry']:
        access_token = await refresh_access_token(email, query['refresh_token'])
    return templates.TemplateResponse(name='hello.html', context={'name': name},request=request)

@app.api_route("/merchant/accounts",methods=['POST','GET'])
async def list_accounts(request:Request,account_id:str=Form(None)):
    url = "https://merchantapi.googleapis.com/accounts/v1/accounts"
    token = request.cookies.get('token')
    if not token:
        return RedirectResponse('/login')

    user=await verify_user(token)
    email=user.get('email')
    name=user.get('name')
    data=await oauth_tokens.find_one({'email':email}) 
    access_token=data['access_token']   
    if not access_token:
        return {"message":'No merchant account'} 

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    message='Accounts not found'
    data = response.json()

    if data.get('error'):
        return templates.TemplateResponse(name='hello.html',context={'name':name,'message':'Account is not google authenticated'},request=request)
    
    if not data:
        await merchant_accounts.update_one({'email':email},{'$set':{'accounts':'No accounts found'}},upsert=True)
        return templates.TemplateResponse(name='hello.html',context={'name':name,'message':message},request=request)
    
    accounts = data["accounts"]
    print(accounts)
    await merchant_accounts.update_one({'email':email},{'$set':{'accounts':accounts}},upsert=True)
    if account_id:
        await merchant_accounts.update_one({'email':email},{'$set':{'selected_account':account_id}})
        selected_id=account_id

    else:
        selected_doc=await merchant_accounts.find_one({'email':email},{'selected_account':1})
        selected_id=selected_doc.get('selected_account') if selected_doc else None
        if not selected_id and accounts:
            selected_id=str(accounts[0]['accountId'])
            await merchant_accounts.update_one({'email':email},{"$set":{'selected_account':selected_id}},upsert=True)

    for acc in accounts:
        if str(acc["accountId"]) == str(selected_id):
            selected_account = acc
            break
    return templates.TemplateResponse(name='hello.html',context={'responses':accounts,'name':name,'selected_account':selected_account,'selected_id':selected_id},request=request)


@app.api_route('/welcome/manual',methods=['POST','GET'])
async def welcome_manual(request:Request):
    token=request.cookies.get('token')
    if not token:
        RedirectResponse('/login')
    try:
        user=await verify_user(token)
        name=user['name']
    except Exception as e:
        raise Exception(e)

    return templates.TemplateResponse(name='hello.html',context={'name':name},request=request)