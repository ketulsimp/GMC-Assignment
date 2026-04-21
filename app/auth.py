"""
Google Authentication Route
For authentication purposes, here used the OAuth library from authlib
Firstly a call is made to the authorization url which in turn gives the auth code from which once the user is authenticated,
redirection is made to the callback url which in turn calls the google token url to get the access and refresh token for the particular user.

These tokens are primarily used when authenticating to any google service on behalf of the user to access user data.
It is not feasible to store these tokens in db and perform session management through them instead for it custom jwt tokens 
need to be created and managed.
"""

from fastapi import APIRouter,Request,HTTPException,Response
from authlib.integrations.starlette_client import OAuth, OAuthError
from app.utils import fetch_data,store_tokens,store_user, user_exists, create_tokens, get_token
from app.settings import settings
from fastapi.responses import RedirectResponse
from app.logger import logger


oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_params={"scope": "openid email profile", "access_type":"offline","prompt":"consent"},
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)

auth_rt = APIRouter(prefix='/auth')

@auth_rt.get('/google/login')
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request,redirect_uri=request.url_for('google_callback'))

@auth_rt.get('/google/callback')
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        if request.is_disconnected():
            raise OAuthError
    except (OAuthError):
        logger.error(msg="Google Authorization error...")
        raise HTTPException(
            status_code=500,
            detail='Google Authentication Failed..'
        )
    # These are access and refresh tokens of google which means they are meant to be used for calling any other
    # google api service on behalf of the user. They are not meant for authorization or authentication.
    google_access_token,google_refresh_token,expires_at,user_info = await fetch_data(token)
    user = await user_exists(user_info.get('email'))
    if not user:
        user_id = await store_user(**user_info,method='google')
        await store_tokens(google_access_token,google_refresh_token,expires_at,str(user_id))
        logger.info(f"Credentials stored for user: {user_id}")
    else:
        await get_token(user)
    logger.info(f"Login Successful for user")
    # headers = {'Set-Cookie': f'access_token=access_token'}
    await create_tokens(user_info.get('email'),request)
    return RedirectResponse(url='/dashboard')

@auth_rt.post('/logout')
async def logout(request: Request):
    del request.session['access-token']
    del request.session['refresh-token']
    logger.info('Token deleted for user')

    
    
    
"""Implementation using google oauth library"""

# from fastapi import APIRouter, Request, Response, Cookie
# from fastapi.responses import RedirectResponse
# import os
# auth_rt = APIRouter(prefix='/auth')

# CLIENT_SECRETS_FILE = 'app/client_secrets.json'

# SCOPES = ["openid email profile"]
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# import google.oauth2.credentials
# import google_auth_oauthlib.flow

# flow = None

# @auth_rt.get('/google/login')
# async def login(request: Request, response: Response):
#     global flow
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,scopes=SCOPES)
#     flow.redirect_uri = request.url_for('callback')
    
#     authrization_url, state = flow.authorization_url(
#         access_type='offline',
#         prompt='consent'
#     )
    
#     response.set_cookie('state',state)
#     return RedirectResponse(url=authrization_url)

# @auth_rt.get('/google/callback')
# async def callback(request: Request):
#     global flow
    
#     authorization_response = str(request.url)
#     print(authorization_response)
#     flow.fetch_token(authorization_response=authorization_response,)
    
#     credentials = flow.credentials
#     print(credentials)
#     return RedirectResponse(url=request.url_for('main'))