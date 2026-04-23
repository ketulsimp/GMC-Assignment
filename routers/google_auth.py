import logging
from datetime import datetime , timedelta
from fastapi import Depends, Request, APIRouter, Response, Form
from utils.schema import TokenResponse
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from utils.db_helper import User,Token,get_db,merchant_account,selected_account_per_user
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

templates = Jinja2Templates(directory="templates")

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


def get_current_user(request: Request, db: Session = Depends(get_db)):
    s_id = request.cookies.get("session_id")

    if not s_id:
        raise HTTPException(status_code=401, detail="Not logged in")

    print(s_id)
    token = db.execute(
        select(Token).where(Token.session_id == s_id)
    ).scalar_one_or_none()

    if not token:
        raise HTTPException(status_code=401, detail="Invalid session")

    # Expiry check
    if token.expires_at < datetime.utcnow():
        return RedirectResponse('/refresh')

    return token


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
        except Exception as e:
            logger.error(f"OAuth token error: {str(e)}")
            return RedirectResponse("/login?error=token_failed")
        
        if request.query_params.get("error") == "access_denied":
            return RedirectResponse("/login?error=cancelled")

        # Session missing
        if "oauth_state" not in request.session:
            return RedirectResponse("/login?error=session_expired")

        # Invalid state
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
            session_id = secrets.token_urlsafe(32)
            token_data = Token(access_token=token['access_token'],session_id=session_id,refresh_token=token['refresh_token'],expires_at=expires_at,user_email=user_info['email'])
            db.add(token_data)
            db.commit()
            
            redirect = RedirectResponse(url='/dashboard')

            redirect.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=True,
                samesite="lax"
            )

        else:
            up = (
            update(Token)
            .values(access_token=token['access_token'],refresh_token=token['refresh_token'],expires_at=expires_at)
            .where(Token.user_email==email)
            )
            db.execute(up)
            db.commit()
            
            result = db.execute(
            select(Token).where(Token.user_email == email)
            )
            
            stored = result.scalar_one_or_none()

            
            redirect = RedirectResponse(url='/dashboard')

            redirect.set_cookie(
                key="session_id",
                value=stored.session_id,
                httponly=True,
                secure=True,
                samesite="lax"
            )
        
        logger.info(f'successfully logging with google for {email}')
        request.session.pop('oauth_state')

        return redirect

    except Exception as e: 
        logger.error('error in google logging ',e)
        return {"error": str(e)}
    
@router.get("/refresh", response_model=TokenResponse)
async def refresh(request : Request,
    db: Session = Depends(get_db)
):
    """REFRESH - Exchanges refresh token for a new access token (ROTATION)"""
    try:
        # Find the token in the database
        session_id = request.cookies.get('session_id')

        result = db.execute(
            select(Token).where(Token.session_id == session_id)
        )
        
        stored = result.scalar_one_or_none()

        if stored is None:
            raise HTTPException(status_code=401, detail={'error': 'Invalid refresh token'})
        
        # Check if token has expired
        if stored.expires_at < datetime.utcnow():
        
            data = {
                "grant_type": "refresh_token",
                "refresh_token": stored.refresh_token,
                "client_id": os.environ['GOOGLE_CLIENT_ID'],
                "client_secret": os.environ['GOOGLE_CLIENT_SECRET'],
            }
            
            async with httpx.AsyncClient() as client:
                result = await client.post("https://oauth2.googleapis.com/token", data=data)
                
            if result is None:
                db.delete(stored)
                db.commit()
                raise HTTPException(status_code=401, detail={'error': 'Refresh token expired'})
            
        
            access_token = result.json()['access_token']
        
            up = (
                update(Token)
                .values(access_token=access_token)
                .where(Token.session_id==session_id)
            )
            db.execute(up)
            db.commit()        
            
        return RedirectResponse('/dashboard')
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f'Refresh error: {error}')
        raise HTTPException(status_code=500, detail={'error': 'Internal server error'})
    
    
@router.get('/dashboard')
async def merchant(req : Request , db : Session = Depends(get_db),user = Depends(get_current_user)):
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(
            "https://merchantapi.googleapis.com/accounts/v1/accounts",
            headers={"Authorization": f"Bearer {user.access_token}"}
        )
        
        if resp is None:
            return {'login again'}
        
    data =  resp.json()
    accounts = data.get("accounts", [])
   
    if not accounts:
        return templates.TemplateResponse(
            req,
            "dashboard.html",
            {
                "accounts": [],
                "error": "No accounts found",
                "selected_account": None
            }
            )
    out = []
   
    for i in accounts:
        
        out.append({
        "accountName": i['accountName'],
        'accountId':i['accountId']
        })
        result = db.execute(
            select(merchant_account).where(merchant_account.accountId == i['accountId'])
        ).scalar_one_or_none()
        
        if result:
            continue
        
        merchant_data = merchant_account(accountName = i['accountName'],
            accountId = i['accountId'],
            email = user.user_email)
        db.add(merchant_data)
        db.commit()
        
        
    selected_account = db.execute(
            select(selected_account_per_user).where(selected_account_per_user.email == user.user_email)
        ).scalar_one_or_none()

    return templates.TemplateResponse(
        req,
        "dashboard.html",
        {
            "accounts": out,
            "selected_account": selected_account
        }
        )

    
@router.post('/selected_account')
def selected_account(accountId : int = Form(...),db:Session = Depends(get_db),user = Depends(get_current_user)):
    merchant_account_data = db.execute(
    select(merchant_account).where(
        merchant_account.accountId == accountId
    )
    ).scalar_one_or_none()
    
    if not merchant_account_data:
        return RedirectResponse('/dashboard', status_code=303)

    
    selected_account = db.execute(
            select(selected_account_per_user).where(selected_account_per_user.email == user.user_email)
        ).scalar_one_or_none()
    
    if selected_account:
        db.delete(selected_account)
        db.commit()
    
    selected_account = selected_account_per_user(email=user.user_email,accountName=merchant_account_data.accountName,accountId=accountId)
    db.add(selected_account)
    db.commit()
    
    return RedirectResponse('/dashboard',status_code=303)