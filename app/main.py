from fastapi import FastAPI
from app.routes.product import product_rt
from contextlib import asynccontextmanager
from app.config.db import connect_to_mongo, disconnect_to_mongo
from app.logs.logger import logger
from asgi_correlation_id import CorrelationIdMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await disconnect_to_mongo()
    
app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(product_rt)   

@app.get('/')
async def main():
    logger.info("Main Route")