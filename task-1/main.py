from fastapi import FastAPI,Request
from starlette.middleware.sessions import SessionMiddleware
from routers.auth import router
from dotenv import load_dotenv

load_dotenv()

app=FastAPI()
app.add_middleware(
    SessionMiddleware, 
    secret_key="@Ashish123"
) 
app.include_router(router)
