from jose import jwt
from datetime import datetime,timedelta
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from config.settings import settings
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY=os.environ['JWT_SECRET_KEY']

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES)
    to_encode.update({'exp':expire,'type':'access'})
    access_token=jwt.encode(to_encode,SECRET_KEY,algorithm=settings.ALGORITHM)
    return access_token

def create_refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
    to_encode.update({'exp':expire,'type':'refresh'})
    refresh_token=jwt.encode(to_encode,SECRET_KEY,algorithm=settings.ALGORITHM)
    return refresh_token

async def verify_user(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[settings.ALGORITHM])
        email=payload.get('sub')
    except:
        pass