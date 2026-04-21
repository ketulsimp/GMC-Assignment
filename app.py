from fastapi import FastAPI

from api.auth import auth
from api.users import user

from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key ='you_secret_key')


app.include_router(auth)
app.include_router(user)


@app.get('/')
def index():
    return {"msg":"Index running"}