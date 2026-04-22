from fastapi import Depends,Request,APIRouter,Form,HTTPException
from dotenv import load_dotenv
import os
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from database.db import users
import bcrypt
import httpx
from database.db import users,oauth_tokens
from utils.jwt import create_access_token,verify_user
from datetime import datetime,timedelta

load_dotenv()

router=APIRouter()

templates=Jinja2Templates(directory='templates')

@router.get('/',response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse(request=request,name='login.html')

@router.get('/register')
async def register(request:Request):
    return templates.TemplateResponse(request=request,name='register.html')

@router.post('/register')
async def register_user(request:Request,name:str=Form(),email:str=Form(),password:str=Form()):
    query=await users.find_one({'email':email})
    if query:
        raise HTTPException(status_code="401",detail='User already exist')
    hashed_pwd=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
    await users.insert_one({"name":name,"email":email,"password":hashed_pwd,'provider':'local'})
    return templates.TemplateResponse(name='login.html',request=request) 


@router.get('/login',response_class=HTMLResponse)
async def manual_login(request:Request):
    return templates.TemplateResponse(request=request,name='login.html')

@router.post('/login')
async def login_user(email:str=Form(),password:str=Form()):
    query=await users.find_one({"email":email})
    if not query or not bcrypt.checkpw(password.encode(),query['password'].encode()):
        raise HTTPException(401,detail='Invalid credentials')
    response=RedirectResponse(url='/welcome/manual')
    token=create_access_token({'sub':email})
    response.set_cookie('token',token,httponly=True)
    return response


GCI=os.getenv('GOOGLE_CLIENT_ID')
TOKEN_REQUEST_URI="https://oauth2.googleapis.com/token"
USER_INFO_URI="https://www.googleapis.com/oauth2/v2/userinfo"
REDIRECT_URL=os.getenv('REDIRECT_URI')


@router.get("/login/google")
async def login():
    url = f"https://accounts.google.com/o/oauth2/auth?client_id={GCI}&redirect_uri={REDIRECT_URL}&response_type=code&scope=openid email profile https://www.googleapis.com/auth/content&access_type=offline&prompt=consent"
    return RedirectResponse(url=url)

@router.get("/google/callback")
async def auth_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(TOKEN_REQUEST_URI,data={
            'code': code,
            'client_id': os.environ['GOOGLE_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': REDIRECT_URL,
            'scope':'https://www.googleapis.com/auth/content',
            'grant_type': 'authorization_code'
        })
        tokens = token_response.json()
        access_token=tokens['access_token']
        refresh_token=tokens['refresh_token']
        user_response=await client.get(USER_INFO_URI,headers={"Authorization":f"Bearer {access_token}"})
        user=user_response.json()
        email=user['email']
        name=user['name']
        query=await users.find_one({'email':email})
        if not query:
            await users.insert_one({'name':user['name'],'email':user['email'],'provider':'google'})
        query2=await oauth_tokens.find_one({'email':email})
        if not query2:
            await oauth_tokens.insert_one({'email':email,'access_token':access_token,'refresh_token':refresh_token,'expiry':datetime.now()+timedelta(seconds=tokens['expires_in'])})

        await oauth_tokens.update_one({'email':email},{"$set":{'access_token':access_token,'refresh_token':refresh_token,'expiry':datetime.now()+timedelta(seconds=tokens['expires_in'])}})
        token=create_access_token({'sub':email})
        response=RedirectResponse(url='/welcome')
        response.set_cookie('token',token,httponly=True)

        return response


@router.get('/switch')
async def switch_account():
    response=RedirectResponse(url='/login/google')
    response.delete_cookie('token')
    return response

@router.get('/logout')
async def logout():
    response=RedirectResponse(url='/login')
    response.delete_cookie('token')
    return response
