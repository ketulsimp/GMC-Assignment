from fastapi import FastAPI
from routes import router
from db import create_db_indexes
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_db_indexes()
app.include_router(router)