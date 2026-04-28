from fastapi import APIRouter,Request
from celery import Celery
from celery.result import  AsyncResult
from app.schema import Product
from typing import List
from db import collection
from log import get_logger


c_app = Celery('c_app',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0'
                )

logger = get_logger()

routes = APIRouter()

@routes.get('/products/batch/{task_id}')
def batch_update(request:Request,task_id: str):
    task_result =  AsyncResult(task_id,app=c_app)
    correlation_id = request.state.correlation_id
    logger.info(f'for id {task_id} status is checked',extra={"correlation_id": correlation_id})
    return {"task_id": task_id, "status": task_result.status, "result": task_result.result} 


@routes.get('/products')
def all_products(req:Request):
    correlation_id = req.state.correlation_id

    logger.info('getting all data from database',extra={"correlation_id": correlation_id})
    data = list(collection.find())
    if not data:
        return 'no data to desplay pls add data first'
    for i in data:
        i['_id']=str(i['_id'])
    # print(data)
    return data


@routes.get('/products/{product_id}')
def one_product(req:Request,product_id:int):
    correlation_id = req.state.correlation_id
    logger.info(f'fetching data for product_id {product_id}',extra={"correlation_id": correlation_id})
    data = collection.find_one({'product_id':product_id})
    if not data:
        return {'msg':'data not found'}
    out = {'product_id' : data['product_id'],
            'name' : data['name'],
            'sku' : data['sku'],
            'photo' : data['photo'],
            'description' : data['description'],
            'gtin' : data['gtin'],
            'price' : data['price'],
            'product_type':data['product_type']
            }
    return out


@routes.post('/products/batch')
def products_regester(req:Request,data : List[Product]):
    correlation_id = req.state.correlation_id
    task = c_app.send_task('celery_task.store_all_product',kwargs={'data':[item.dict() for item in data],'correlation_id':correlation_id})
    correlation_id = req.state.correlation_id
    logger.info(f'for storing new data, task send to id {task.id}',extra={"correlation_id": correlation_id})
    return {"task_id": task.id}
    