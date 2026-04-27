from fastapi import FastAPI,Response,Request, HTTPException
from app.routes.product import product_rt
from contextlib import asynccontextmanager
from app.config.db import connect_to_mongo, disconnect_to_mongo
from asgi_correlation_id import CorrelationIdMiddleware
from pymongo.errors import PyMongoError
from app.logs.logger import web_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await disconnect_to_mongo()
    
app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

@app.exception_handler(PyMongoError)
async def handling_pymongo_error(request, exc):
    web_logger.exception(f"Database Error...")
    raise HTTPException(status_code=500, detail='Internal Server Error.')

@app.exception_handler(500)
async def handling_pymongo_error(request, exc):
    web_logger.exception(f"Server Error...")
    return Response()