from fastapi import APIRouter, Path, Body, Request
from typing import Annotated, List
from app.models.product_model import Product
from app.services.product_service import fetch_products, fetch_product_by_id
from app.utilities.product_utils import check_similarity, serialize
from fastapi.responses import JSONResponse
import json
from app.config.celery_client import celery
from product_batch_logger.web_logger import web_logger
from asgi_correlation_id import correlation_id

product_rt = APIRouter(prefix='/products')

@product_rt.get('/')
async def get_all_products():
    return await fetch_products()

@product_rt.get('/{id}')
async def get_product_by_id(id: Annotated[str,Path()]):
    products = await fetch_product_by_id(id)
    return products

@product_rt.post('/insert')
async def insert_products(request: Request,  products: Annotated[List[Product],Body(max_length=10000)]):
    result = check_similarity(products)
    if result is not None:
        return JSONResponse(
            content=result,
            status_code=422
        )
    docs = serialize(products)
    task = celery.send_task('batch_store_in_mongo',args=[docs,correlation_id.get()],queue='new-queue')
    return task.id

@product_rt.get('/batch/status')
async def get_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state=='FAILURE':
        meta = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)))
        return (task.state,{'faultyProducts':meta['result'].get('faulty_products')})
    return task.state