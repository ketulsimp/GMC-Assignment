from fastapi import Depends,Request,APIRouter,Form,HTTPException
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
import os
from fastapi.templating import Jinja2Templates
from database.db import users
import bcrypt
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests

load_dotenv()

router=APIRouter()

oauth=OAuth()

oauth.register(
    name='google',
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_params={"scope": "openid email profile"}
)

templates=Jinja2Templates(directory='templates')

@router.get('/')
async def home(request:Request):
    return templates.TemplateResponse(request=request,name='login.html')

@router.post('/register')
async def register(request:Request,name:str=Form(),email:str=Form(),password:str=Form()):
    hashed_pwd=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
    await users.insert_one({"name":name,"email":email,"password":hashed_pwd})
    return templates.TemplateResponse('login.html',{'request':request}) 

@router.post('/login')
async def login(request:Request,email:str=Form(),password:str=Form()):
    query=await users.find_one({"email":email})
    if query:
        return templates.TemplateResponse('hello.html',{'request':request})
    return templates.TemplateResponse(request=request,name='register.html')


GCI=os.getenv('GOOGLE_CLIENT_ID')

@router.get("/login/google")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    print(redirect_uri)
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GCI}&redirect_uri={redirect_uri}&response_type=code&scope=openid email profile"
    # return await oauth.google.authorize_redirect(request=request,redirect_uri=google_auth_url)
    return RedirectResponse(url=google_auth_url)

@router.get("/google/callback")
async def auth_callback(code: str, request: Request):
    print("HELLO")
    token_request_uri = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': os.environ['GOOGLE_CLIENT_ID'],
        'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
        'redirect_uri': request.url_for('auth_callback'),
        'grant_type': 'authorization_code',
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_request_uri, data=data)
        response.raise_for_status()
        token_response = response.json()
    id_token_value = token_response.get('id_token')
    if not id_token_value:
        raise HTTPException(status_code=400, detail="Missing id_token in response.")

    try:
        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GCI)
        name = id_info.get('name')
        request.session['user_name'] = name
        return RedirectResponse(url=request.url_for('welcome'))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid id_token: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/welcome")
async def welcome(request: Request):
    name = request.session.get('user_name', 'Guest')
    context = {"request": request, "name": name}
    return templates.TemplateResponse(request=request,name="hello.html",context=context )