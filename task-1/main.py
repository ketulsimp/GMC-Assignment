from fastapi import FastAPI,Request,Depends,HTTPException
from routers.auth import router
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from database.db import users,oauth_tokens
from fastapi.templating import Jinja2Templates
from utils.jwt import verify_user,verify_manual_user
from datetime import datetime,timedelta,timezone
from utils.refresh import refresh_access_token
import requests

load_dotenv()

app=FastAPI()

app.include_router(router)
templates=Jinja2Templates(directory='templates')

@app.get('/welcome')
async def welcome_google(request:Request):
    token=request.cookies.get('token')
    if not token:
        RedirectResponse('/login')
    payload=await verify_user(token)
    email=payload.get('email')
    name=payload.get('name')
    query=await oauth_tokens.find_one({'email':email})
    if datetime.now()>query['expiry']:
        refresh_access_token(email,query['refresh_token'])
    return templates.TemplateResponse(name='hello.html',context={'name':name},request=request)



@app.get("/merchant/accounts")
async def list_accounts(request:Request):
    url = "https://merchantapi.googleapis.com/accounts/v1/accounts"
    token=request.cookies.get('token')
    payload=await verify_user(token)
    email=payload.get('email')
    name=payload.get('name')
    data=await oauth_tokens.find_one({'email':email}) 
    access_token=data['access_token']   
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    message='Accounts not found'
    data = response.json()
    if not data:
        return templates.TemplateResponse(name='hello.html',context={'name':name,'message':message},request=request)
    
    accounts = data["accounts"]

    return templates.TemplateResponse(name='hello.html',context={'responses':accounts,'name':name},request=request)


@app.get('/welcome/manual')
async def welcome_manual(request:Request,user:dict=Depends(verify_manual_user)):
    token=request.cookies.get('token')
    print(user)
    if not token:
        RedirectResponse('/login')
    try:
        payload=await verify_user(token)
        name=payload.get('name')
    except Exception as e:
        raise Exception(e)

    return templates.TemplateResponse(name='hello.html',context={'name':name},request=request)