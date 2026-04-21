from utils.oauth import oauth
import os
from starlette.middleware.base import BaseHTTPMiddleware 
from fastapi import Request
from fastapi.exceptions import HTTPException
from db.get_client import db
from db.users import update_access_token
from datetime import datetime, timedelta
from bson import ObjectId
from utils.logger import logger
import httpx
import ast


async def check_token_expiry(request:Request): 
        logger.info('Entered middleware')

        user = request.session['user']
        
        if user:

            tok = await db.tokens.find_one({'user_id':user})

            if tok:
                if tok.get('expiry') < datetime.now():
                    
                    
                    async with httpx.AsyncClient() as client:
                         
                        res = await client.post('https://oauth2.googleapis.com/token',data={
                              'client_id':os.environ['GOOGLE_CLIENT_ID'],
                              'client_secret':os.environ['GOOGLE_CLIENT_SECRET'],
                              'refresh_token': tok.get('refresh_token'),
                              'grant_type': 'refresh_token'
                         },
                        headers={
                               'Content-Type': "application/x-www-form-urlencoded"
                         }
                         
                         )
                        res = res.json()
                        access_token = res.get('access_token')
                        expiry = datetime.now() + timedelta(res.get('expires_in'))                         

                        await update_access_token(refresh_token=tok.get('refresh_token'),access_token=access_token,expiry=expiry)

                        return res
                else:
                     print('valid Token')
            else:
                print('Token not found')

                return HTTPException(401,'Token not found in database')
    

        else:
            print('Token not found')

            return HTTPException(401,'Token not found')
    
