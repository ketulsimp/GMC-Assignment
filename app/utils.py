from app.db import get_mongo_db
from datetime import datetime
from fastapi import HTTPException, Cookie, Request
import httpx
from app.settings import settings
from app.logger import logger as logger
import jwt
from jwt.exceptions import ExpiredSignatureError
from fastapi.responses import RedirectResponse

async def user_exists(email:str):
    db = get_mongo_db()
    if user:= await db.users.find_one({'email': email}):
        return str(user['_id'])
    return None

async def refresh_token(refresh_token):
    params = {
        'client_id': settings.google_client_id,
        'client_secret': settings.google_client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://oauth2.googleapis.com/token",params=params)
        new_token = response.json()
        return (new_token.get('access_token'),new_token.get('expires_in'))

async def get_token(user_id):
    db = get_mongo_db()
    token_data = await db.oauth_tokens.find_one({'user': user_id})
    if token_data:
        if token_data.get('expires_at') < datetime.now().timestamp():
            new_access_token,time_limit = await refresh_token(token_data.get('refresh_token'))
            await db.oauth_tokens.update_one({'user': user_id}, {"$set": {'access_token': new_access_token, 'expires_at': datetime.now().timestamp() + time_limit}})
            logger.info(f"New Access Token set for user_id: {user_id}")
            return new_access_token
        return token_data.get('access_token')
    raise HTTPException(status_code=500, detail='Token does not exist.')

async def fetch_data(payload):
    access_token = payload.get('access_token')
    refresh_token = payload.get('refresh_token')
    expires_at = payload.get('expires_at')
    user_info = {
        'name': payload['userinfo'].get('name'),
        'email': payload['userinfo'].get('email')
    }
    return (access_token,refresh_token,expires_at,user_info)

async def store_user(name,email,method):
    db = get_mongo_db()
    doc = {
        'name': name,
        'email': email,
        'method': method
    }
    result = await db.users.insert_one(doc)
    return result.inserted_id

async def store_tokens(access_token,refresh_token,expires_at,user_id):
    db = get_mongo_db()
    token_data = {
        'user': user_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at
    }
    await db.oauth_tokens.insert_one(token_data)
    
async def create_tokens(user_email, request: Request):
    access_token =  jwt.encode({'sub':user_email},settings.secret_key,algorithm="HS256")
    refresh_token = jwt.encode({'sub':user_email},settings.secret_key,algorithm="HS256")
    # response.set_cookie('access_token',access_token)
    # response.set_cookie('refresh_token',refresh_token)
    request.session['access-token'] = access_token
    request.session['refresh-token'] = refresh_token
    logger.info("Session based tokens created")

async def authenticate(request: Request):
    access_token = request.session.get('access-token')
    refresh_token = request.session.get('refresh-token')
    try:
        user = jwt.decode(access_token,settings.secret_key,algorithms=["HS256"])
        return user['sub']
    except ExpiredSignatureError:
        try:
            user = jwt.decode(refresh_token,settings.secret_key,algorithms=["HS256"])
            # response.set_cookie('access_token',jwt.encode({'sub':user['sub']},settings.secret_key,algorithm="HS256"))
            request.session['access-token'] = jwt.encode({'sub':user['sub']},settings.secret_key,algorithm="HS256")
            return user['sub']
        except:
            logger.error("Authentication Failed")
            return RedirectResponse(url='/auth/google/login')
    except Exception:
        logger.error("Authentication Failed")
        return RedirectResponse(url='/auth/google/login')

            

