from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.db import connect_to_mongo, disconnect_to_mongo
from app.auth import auth_rt
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.utils import get_token, authenticate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await disconnect_to_mongo()
    

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key = "This_is_a_secret_key")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
app.include_router(auth_rt)

@app.get('/dashboard')
async def main(user=Depends(authenticate)):
    return f"Welcome To Dashboard {user}"
    
@app.get('/check')
async def check(user_id: str):
    token = await get_token(user_id)
    return token

