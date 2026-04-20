from fastapi import FastAPI
from api.auth import auth
from dotenv import load_dotenv

load_dotenv()



app = FastAPI()

app.include_router(auth)

@app.get('/')
def index():
    return {"msg":"Index running"}