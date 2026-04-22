import logging
from datetime import datetime , timedelta
from fastapi import Depends, Request, APIRouter, Response
from utils.schema import TokenResponse,RefreshRequest
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from utils.db_helper import User,Token,get_db
from authlib.integrations.starlette_client import OAuth
import os
import httpx
from dotenv import load_dotenv
import secrets

load_dotenv()

router = APIRouter()

logger = logging.getLogger("SimpleLogger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
logger.addHandler(file_handler)




# Configure OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"scope": "openid email profile https://www.googleapis.com/auth/content"},
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile https://www.googleapis.com/auth/content"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)


# Redirect user to Google for authentication
@router.get("/auth/google")
async def auth_google(request: Request):
    logger.info('logging attempt with google')
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri="http://127.0.0.1:8000/auth/google/callback",
        state=state,
        prompt="consent",
        access_type="offline"
    )

# Handle the OAuth callback from Google
@router.get("/auth/google/callback")
async def google_callback(request: Request,res: Response,db: Session = Depends(get_db)):
    try:
        try:
            token = await oauth.google.authorize_access_token(request)
        except Exception:
            return RedirectResponse("/login?error=token_failed")
        
        if request.query_params.get("error") == "access_denied":
            return RedirectResponse("/login?error=cancelled")

        # 2. Session missing
        if "oauth_state" not in request.session:
            return RedirectResponse("/login?error=session_expired")

        # 3. Invalid state
        if request.query_params.get("state") != request.session.get("oauth_state"):
            return RedirectResponse("/login?error=invalid_state")

        user_info = token.get("userinfo")
        if not user_info:
            return RedirectResponse("/login?error=userinfo_failed")
            
        email = user_info.get('email')
        if not email:
            return {'msg':'email not found'}
        
        result = db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(name=user_info['given_name'],email=user_info['email'])
            db.add(user)
            db.commit()
        

        token_data = db.execute(
            select(Token).where(Token.user_email == email)
        )
        token_data_from_db = token_data.scalar_one_or_none()
        expires_at = datetime.utcnow() + timedelta(seconds=token['expires_in'])
        if token_data_from_db is None:
            # token_data = Token(access_token=token['access_token'],refresh_token=token['refresh_token'],expires_at=expires_at,user_email=user_info['email'])
            token_data = Token(access_token=token['access_token'],refresh_token=token['refresh_token'],expires_at=expires_at,user_email=user_info['email'])
            db.add(token_data)
            db.commit()
        else:
            up = (
            update(Token)
            .values(access_token=token['access_token'],refresh_token=token['refresh_token'],expires_at=expires_at)
            .where(Token.user_email==email)
            )
            db.execute(up)
            db.commit()
            
        
        logger.info(f'successfully logging with google for {email}')
        
        res.set_cookie(
        key="session_id", value=token['refresh_token'], httponly=True, secure=True, samesite="lax")

        return RedirectResponse(url='/dashboard')



    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())  
        logger.error('error in google logging')
        return {"error": str(e)}
    
@router.post("/refresh", response_model=TokenResponse)
async def refresh(request : Request,
    req: RefreshRequest,
    db: Session = Depends(get_db)
):
    """REFRESH - Exchanges refresh token for a new access token (ROTATION)"""
    try:
        # Find the token in the database
        result = db.execute(
            select(Token).where(Token.refresh_token == req.refreshToken)
        )
        
        session_id = request.cookies.get('session_id')

        stored = result.scalar_one_or_none()

        if stored is None:
            raise HTTPException(status_code=401, detail={'error': 'Invalid refresh token'})
        
        # Check if token has expired
        if stored.expires_at < datetime.utcnow():
            db.delete(stored)
            db.commit()
            raise HTTPException(status_code=401, detail={'error': 'Refresh token expired'})
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": req.refreshToken,
            "client_id": os.environ['GOOGLE_CLIENT_ID'],
            "client_secret": os.environ['GOOGLE_CLIENT_SECRET'],
        }
        
        async with httpx.AsyncClient() as client:
            result = await client.post("https://oauth2.googleapis.com/token", data=data)
        
        
        access_token = result.json()['access_token']
        
        up = (
            update(Token)
            .values(access_token=access_token)
            .where(Token.refresh_token==req.refreshToken)
        )
        db.execute(up)
        db.commit()        
        
        return {'access_token':access_token}
        
    except HTTPException:
        raise
    # except Exception as error:
    #     logger.error(f'Refresh error: {error}')
    #     raise HTTPException(status_code=500, detail={'error': 'Internal server error'})
    
    
@router.get('/dashboard')
def dash():
    return {'msg':'welcome to dashboard'}