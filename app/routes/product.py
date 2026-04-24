from fastapi import APIRouter, Path, Body
from typing import Annotated, List
from app.models.product_model import Product
from app.services.product_service import fetch_products, fetch_product_by_id
from app.utilities.product_utils import check_similarity, serialize
from fastapi.responses import JSONResponse
from app.tasks.task import batch_store_in_mongo
from app.tasks.task import celery
import json

product_rt = APIRouter(prefix='/products')


@product_rt.get('/')
async def get_all_products():
    return await fetch_products()

@product_rt.get('/{id}')
async def get_product_by_id(id: Annotated[str,Path()]):
    return await fetch_product_by_id(id)


@product_rt.post('/insert')
async def insert_products(products: Annotated[List[Product],Body(max_length=1000)]):
    result = check_similarity(products)
    if result is not None:
        return JSONResponse(
            content=result,
            status_code=422
        )
    docs = serialize(products)
    print(docs)
    task = batch_store_in_mongo.apply_async(args=[docs])
    return task.id

@product_rt.get('/batch/status')
async def get_status(task_id):
    task = celery.AsyncResult(task_id)
    if task.state=='FAILURE':
        meta = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)))
        return (task.state,{'faultyProducts':meta['result'].get('faulty_products')})
    return task.state