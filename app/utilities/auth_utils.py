from app.config.db import get_mongo_db
from datetime import datetime,timedelta
from fastapi import HTTPException, Cookie, Request
import httpx
from app.config.settings import settings
from app.log.logger import logger as logger
import jwt
from jwt.exceptions import ExpiredSignatureError
from app.error.exceptions import TokenNotFoundError

async def user_exists(email:str):
    db = get_mongo_db()
    user = await db.users.find_one({'email': email})
    return str(user.get('_id')) if user else None
    
async def token_exists(user: str):
    db = get_mongo_db()
    doc = await db.oauth_tokens.find_one({'user':user})
    return True if doc else False

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
    raise TokenNotFoundError

async def fetch_token(user_id):
    db = get_mongo_db()
    doc = await db.oauth_tokens.find_one_and_delete({'user':user_id})
    if token:= doc.get('access_token'):
        return token
    raise TokenNotFoundError

async def fetch_data(payload):
    access_token = payload.get('access_token')
    print(access_token)
    refresh_token = payload.get('refresh_token')
    expires_at = payload.get('expires_in') + datetime.now().timestamp()
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
    return str(result.inserted_id)

async def store_tokens(access_token,refresh_token,expires_at,user_id):
    db = get_mongo_db()
    token_data = {
        'user': user_id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at
    }
    await db.oauth_tokens.replace_one({'user':user_id},token_data,upsert=True)
    
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
            request.session['access-token'] = jwt.encode({'sub':user['sub'],'exp':timedelta(minutes=10)},settings.secret_key,algorithm="HS256")
            return user['sub']
        except:
            logger.error("Authentication Failed")
            raise HTTPException(status_code=403)
    except Exception:
        logger.error("Authentication Failed")
        raise HTTPException(status_code=403)
    
async def delete_user_credentials(request: Request):
    user = request.session.pop('user',None)
    request.session.clear()
    return user
    

            

