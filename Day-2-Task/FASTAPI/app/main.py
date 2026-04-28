from fastapi import FastAPI,Response,Request, HTTPException
from app.routes.product import product_rt
from contextlib import asynccontextmanager
from app.config.db import connect_to_mongo, disconnect_to_mongo
from asgi_correlation_id import CorrelationIdMiddleware
from pymongo.errors import PyMongoError
from product_batch_logger.web_logger import web_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await disconnect_to_mongo()
    
app = FastAPI(lifespan=lifespan)
@app.middleware('http')
async def middleware(request: Request,call_next):
    print(request.url.__str__())
    web_logger.info("Request started")
    response = await call_next(request)
    web_logger.info("Request Ended")
    return response

app.add_middleware(CorrelationIdMiddleware)
app.include_router(product_rt)


@app.exception_handler(PyMongoError)
async def handling_pymongo_error(request, exc):
    web_logger.exception(f"Database Error...")
    raise HTTPException(status_code=500, detail='Internal Server Error.')


@app.exception_handler(Exception)
async def handling_pymongo_error(request, exc: Exception):
    print(request.url.__str__())
    web_logger.exception(f"Exception")
    raise HTTPException(status_code=500, detail='Internal Server Error.')

