from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse
from typing import Annotated
from fastapi.templating import Jinja2Templates
from db.get_client import client
from dotenv import load_dotenv
import os

load_dotenv()

import google.oauth2.credentials
import google_auth_oauthlib.flow as oauth_flow


templates = Jinja2Templates(directory='templates')

scopes = ["https://www.googleapis.com/auth/content", "https://www.googleapis.com/auth/userinfo.profile","https://www.googleapis.com/auth/userinfo.email", "openid"]

auth = APIRouter(prefix='/api/auth')

REDIRECT_URI = 'http://localhost:8000/api/auth/callback'

@auth.get('/login')
def login(request: Request):

    return templates.TemplateResponse(
        request=request, name='login.html',context={"id":os.getenv('CLIENT_ID')}
    )



@auth.get('/authorize')
async def authorize(response: RedirectResponse):


    flow = oauth_flow.Flow.from_client_secrets_file('client_secret.json',scopes=scopes,code_verifier='asbkasjdfbksjbdsjdbskdbsdjbsdkjbsdbsjdbsjbfljsjhsdfkjad')

    try:

        flow.redirect_uri = REDIRECT_URI

        auth_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
        print("Auth URL ",auth_url," state ",state)
        


        return RedirectResponse(auth_url)

    except Exception as e:
        print(e)



@auth.get('/callback')
async def callback(request:Request, state: str|None =None, code: str|None =None):
    try:


        flow = oauth_flow.Flow.from_client_secrets_file('client_secret.json',scopes=scopes,state=state,code_verifier='asbkasjdfbksjbdsjdbskdbsdjbsdkjbsdbsjdbsjbfljsjhsdfkjad')


        flow.redirect_uri = REDIRECT_URI

        print(flow.client_config)
        temp_var = str(request.url)
        if "http:" in temp_var:
            temp_var = "https:" + temp_var[5:]
        
        auth_res = temp_var

        auth_res = str(auth_res)

        auth_res = auth_res+"&grant_type='authorization_code'"


        flow.fetch_token(authorization_response=auth_res)

        print(flow)


        credentials = flow.credentials

        cred_dict = credentials_to_dict(credentials=credentials) 
        
        print(cred_dict)


        
        tokens = client['oauth_tokens']

        

        tokens.insert_one(
            {
          'access_token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'expiry':credentials.expiry,
          'client_id':credentials.client_id
          }
        )     



        return RedirectResponse('/')

    except Exception as e:
        
        print(e)





def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'granted_scopes': credentials.granted_scopes,
          'expiry':credentials.expiry,
          'client_id':credentials.client_id
          }

