from jose import jwt
import os
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException
from config.settings import settings
from dotenv import load_dotenv
from database.db import users

load_dotenv()

security=HTTPBearer()

SECRET_KEY=os.environ['JWT_SECRET_KEY']

def create_access_token(data:dict):
    to_encode=data.copy()
    access_token=jwt.encode(to_encode,SECRET_KEY,algorithm=settings.ALGORITHM)
    return access_token

def create_refresh_token(data:dict):
    to_encode=data.copy()
    refresh_token=jwt.encode(to_encode,SECRET_KEY,algorithm=settings.ALGORITHM)
    return refresh_token

async def verify_user(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token=credentials
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[settings.ALGORITHM])
        email=payload.get('sub')
        if email is None:
            raise HTTPException(status_code=401,detail='Invalid token')
    except Exception as e:
        raise Exception(e)
    user=await users.find_one({'email':email})
    return user

async def verify_manual_user(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token=credentials.credentials
    print("MANUALTOKEN")
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[settings.ALGORITHM])
        email=payload.get('sub')
        if email is None:
            raise HTTPException(status_code=401,detail='Invalid Token')
    except Exception:
        raise HTTPException(401, 'Invalid token')
    user=await users.find_one({'email':email})
    return user