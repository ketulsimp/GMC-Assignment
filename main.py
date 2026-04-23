from routers import  google_auth
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Session Middleware(Needed for OAuth)
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.environ['SECRET_KEY']
)  

# Registering Routers
app.include_router(google_auth.router)

# Root Endpoint
@app.get("/")
def home():
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())
