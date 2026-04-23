from jose import jwt
import os
from fastapi.security import HTTPBearer
from fastapi import HTTPException
from config.settings import settings
from dotenv import load_dotenv
from database.db import users,oauth_tokens

load_dotenv()

security=HTTPBearer()

SECRET_KEY=os.environ['JWT_SECRET_KEY']

def create_access_token(data:dict):
    to_encode=data.copy()
    expiry=settings.ACCESS_TOKEN_EXPIRY_MINUTES
    to_encode.update({'expiry':expiry})
    access_token=jwt.encode(to_encode,SECRET_KEY,algorithm=settings.ALGORITHM)
    return access_token

def create_refresh_token(data:dict):
    to_encode=data.copy()
    expiry=settings.REFRESH_TOKEN_EXPIRY_DAYS
    to_encode.update({'expiry':expiry})
    refresh_token=jwt.encode(to_encode,SECRET_KEY,algorithm=settings.ALGORITHM)
    return refresh_token

async def verify_user(token:str):
    try:
        query=await oauth_tokens.find_one({'access_token':token})
        email=query['email']
        if email is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        
    except Exception as e:
        raise HTTPException(status_code=401, detail='Invalid token')

    user = await users.find_one({'email': email})
    return user
