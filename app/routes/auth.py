"""
Google Authentication Route
For authentication purposes, here used the OAuth library from authlib
Firstly a call is made to the authorization url which in turn gives the auth code from which once the user is authenticated,
redirection is made to the callback url which in turn calls the google token url to get the access and refresh token for the particular user.

These tokens are primarily used when authenticating to any google service on behalf of the user to access user data.
It is not feasible to store these tokens in db and perform session management through them instead for it custom jwt tokens 
need to be created and managed.
"""

from fastapi import APIRouter,Request,HTTPException,Depends
from authlib.integrations.starlette_client import OAuth, OAuthError
from app.utilities.auth_utils import fetch_data,store_tokens,store_user, user_exists, create_tokens, fetch_token, delete_user_credentials, authenticate
from app.config.settings import settings
from fastapi.responses import RedirectResponse
from app.log.logger import logger
import httpx
from app.error.exceptions import TokenNotFoundError


oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_params={"scope": "openid email profile https://www.googleapis.com/auth/content", "access_type":"offline","prompt":"consent"},
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)

auth_rt = APIRouter(prefix='/auth')
print(oauth.register)

@auth_rt.get('/google/login')
async def google_login(request: Request):
    """
    This route is called when sign in with google is initiated from the frontend.
    """
    
    return await oauth.google.authorize_redirect(request,redirect_uri=request.url_for('google_callback'))    

@auth_rt.get('/google/callback')
async def google_callback(request: Request):
    """
    This is the callback route configured to obtain tokens in exchange of code.
    """
    
    try:
        token = await oauth.google.authorize_access_token(request)
        if await request.is_disconnected():
            print(await request.is_disconnected)
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
    user_id = await user_exists(user_info.get('email'))
    if not user_id:
        user_id = await store_user(**user_info,method='google')
    await store_tokens(google_access_token,google_refresh_token,expires_at,str(user_id))
    request.session['user'] = user_id
    logger.info(f"Credentials stored for user: {user_id}")
    logger.info(f"Login Successful for user")
    # headers = {'Set-Cookie': f'access_token=access_token'}
    await create_tokens(user_info.get('email'),request)
    return RedirectResponse(url=str(request.base_url))

@auth_rt.get('/hard-logout')
async def hard_logout(request: Request,user = Depends(authenticate)):
    """
    Logouts user session and revokes google tokens too.
    """
    
    user = await delete_user_credentials(request)
    try:
        token = await fetch_token(user)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url='https://oauth2.googleapis.com/revoke',
                params={'token':token},
                headers={'content-type':'application/x-www-form-urlencoded'}
            )
        if response.status_code==200:
            logger.info(f"Token successfully deleted for user {user}")
            logger.info(f"Hard Logout Successfull for user {user}")
        else:
            logger.error(f"Token deletion unsuccessfull")
    except TokenNotFoundError:
        pass
    return RedirectResponse(url=request.url_for('home'))
    
        
@auth_rt.get('/soft-logout')
async def soft_logout(request: Request):
    """
    Only logout user sessions.
    """
    
    user = await delete_user_credentials(request)
    return RedirectResponse(url=request.url_for('home'))
        
@auth_rt.get('/change-account')
async def change_account(request: Request,user = Depends(authenticate)):
    """
    Requires a account to be logged in to call this route.
    Change google account; if process fails fallback to previously logged in account.
    """
    
    return RedirectResponse(url=request.url_for('google_login'))

    

    
# """Implementation using google oauth library"""

# from fastapi import APIRouter, Request, Response, Cookie
# from fastapi.responses import RedirectResponse
# import os
# import google.oauth2.credentials
# import google_auth_oauthlib.flow

# auth_rt = APIRouter(prefix='/auth')

# CLIENT_SECRETS_FILE = 'app/client_secrets.json'

# SCOPES = ["openid email profile"]
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


# @auth_rt.get('/google/login')
# async def login(request: Request, response: Response):
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,scopes=SCOPES)
#     flow.redirect_uri = request.url_for('callback')
    
#     authrization_url, state = flow.authorization_url(
#         access_type='offline',
#         prompt='consent'
#     )
#     code_verifier = flow.code_verifier
#     request.session['state'] = state
#     request.session['code_verifier'] = code_verifier
#     return RedirectResponse(url=authrization_url)

# @auth_rt.get('/google/callback')
# async def callback(request: Request):
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE,scopes=SCOPES,state=request.session['state'])
#     flow.code_verifier = request.session['code_verifier']
#     flow.redirect_uri = request.url_for('callback')
    
#     authorization_response = str(request.url)
#     print(authorization_response)
#     flow.fetch_token(authorization_response=authorization_response)
    
#     credentials = flow.credentials
#     del request.session['state']
#     del request.session['code_verifier']
#     print(credentials)
#     return RedirectResponse(url=request.url_for('main'))