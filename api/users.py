from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from utils.middleware import check_token_expiry
from typing import Annotated
import httpx

import os
from utils.logger import logger

user = APIRouter(prefix='/api')

templates = Jinja2Templates(directory='templates')

@user.get('/me')
async def dashboard(request:Request,token: Annotated[str, Depends(check_token_expiry)]):
    try:
        if user:= request.session['user']:

            print(type(user))

            return templates.TemplateResponse(
                    request=request, name='dashboard.html',context={"user":user}
                )
        else:
            return templates.TemplateResponse(
                request=request,name='login.html'
            )

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc()) 
        logger.warning(str(e))
        return {"error": str(e)}


@user.get('/revoke')
async def revoke_token(request:Request,token: Annotated[str, Depends(check_token_expiry)]):
    try:
        if user:= request.session['user']:
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
            return templates.TemplateResponse(
                    request=request, name='dashboard.html',context={"user":user}
                )
        else:
            return templates.TemplateResponse(
                request=request,name='login.html'
            )

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc()) 
        logger.warning(str(e))
        return {"error": str(e)}




@user.get('/logout')
async def logout(request:Request):
    try:
        request.session.pop('user')
        return RedirectResponse('/api/auth/login')

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc()) 
        logger.warning(str(e))
        return {"error": str(e)}




