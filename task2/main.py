from fastapi import FastAPI
from task2.routes.router import router

app=FastAPI()
app.include_router(router)
