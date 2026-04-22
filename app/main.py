from fastapi import FastAPI, Depends, Response
from contextlib import asynccontextmanager
from app.config.db import connect_to_mongo, disconnect_to_mongo
from app.routes.auth import auth_rt
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.utilities.utils import get_token, authenticate
from app.config.settings import settings


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

@app.get('/dashboard')
async def main(user = Depends(authenticate)):
    # await create_tokens(user_info.get('email'),request)
    return f"Welcome To Dashboard {user}"
    
@app.get('/check')
async def check(user_id: str):
    token = await get_token(user_id)
    print("Hello world")
    return token

