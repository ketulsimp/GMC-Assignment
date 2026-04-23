from fastapi import FastAPI, Depends, Request, Header
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.config.db import connect_to_mongo, disconnect_to_mongo
from app.routes.auth import auth_rt
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.utilities.auth_utils import get_token, authenticate
from app.config.settings import settings
from app.routes.merchant import merchants_rt
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates('app/templates')

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await disconnect_to_mongo()
    

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)
# app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1/5500"],allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"])
app.include_router(auth_rt)
app.include_router(merchants_rt)

@app.get('/home')
async def home(request: Request):
    return templates.TemplateResponse(request=request, name='home.html',context={'msg': request.session.pop('Unauthorized',None)})
@app.get('/')
async def main(request: Request, user = Depends(authenticate)):
    # await create_tokens(user_info.get('email'),request)
    return templates.TemplateResponse(
        request=request,
        name='dashboard.html',
        context={'user': user}
    )
    
@app.get('/check')
async def check(user_id: str):
    token = await get_token(user_id)
    print("Hello world")
    return token

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name='404_error.html',
        status_code=404
    )

@app.exception_handler(400)
async def some_error(request: Request, exc):
    return RedirectResponse(
        url=request.url_for('get_all_merchants')
    )
    
@app.exception_handler(403)
async def unauthorized_error(request: Request, exc):
    request.session['Unauthorized'] = True
    return RedirectResponse(
        url=request.url_for('home')
    )