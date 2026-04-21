from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse
from typing import Annotated
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from db.users import insert_google_acc_to_db, insert_token_to_db, insert_user_to_db
from utils.oauth import oauth
from schemas.auth import User, Google_Accounts, OAuthToken
from datetime import datetime, timedelta
import requests
import os
from utils.logger import logger

load_dotenv()


templates = Jinja2Templates(directory='templates')

auth = APIRouter(prefix='/api/auth')


@auth.get('/login')
def login(request: Request):
    
    logger.info('Started User Login')

    return templates.TemplateResponse(
        request=request, name='login.html'
    )





@auth.get('/google/login')
async def authorize(request: Request):
    try:
        logger.info('Started Google Login')        
        return await oauth.google.authorize_redirect(request, redirect_uri=os.environ['REDIRECT_URL'],access_type="offline",prompt="consent")

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())  # Debugging step

        logger.warning(str(e))

        return {"error": str(e)}

    



@auth.get('/google/callback')
async def callback(request:Request,state: str|None = None , code: str|None =None, error: str|None = None):
    try:
        print('callback called')
        
        if error:
            return templates.TemplateResponse(
        request=request, name='error.html',context={'msg':str(error)}
    )

        logger.info('Code Recevied Starting Acesssing token')

        token = await oauth.google.authorize_access_token(request)
  
        logger.info('Token Recevied Starting Parsing Token for user')

        user = await oauth.google.parse_id_token(request, token)
        
        logger.info('User parsed. Starting DB Ops')

        print(token)

        res = await insert_user_to_db(User(email=user.email,name=user.name))
        print(res)

        res1 = await insert_google_acc_to_db(Google_Accounts(email=user.email,name=user.name,picture=user.picture))

        exp = datetime.now() + timedelta(seconds = token.get('expires_in'))
        print(res1)


        res3 = await insert_token_to_db(OAuthToken(access_token=token.get('access_token'),refresh_token=token.get('refresh_token'),expiry=exp,user_id=str(res)))

        print(res3)
        
        
        print(user)

        usr = {
            'id':res,
            'name':user.name,
            'email':user.email,
            'picture':user.picture
        }

        request.session['user'] = str(res)
        
        return RedirectResponse('/api/me')

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())  # Debugging step

        logger.warning(str(e))

        return {"error": str(e)}


