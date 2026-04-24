from fastapi import APIRouter
from celery.result import  AsyncResult
from app.celery.celery_app import c_task
from app.service.schema import Product
from typing import List
from app.celery.celery_task import store_all_product
from app.db import collection
import logging

logging.basicConfig(
    level=logging.INFO,
     filename="app.log",
     encoding="utf-8",
     filemode="a",
     format="{asctime} - {levelname} - {message}",
     style="{",
     datefmt="%Y-%m-%d %H:%M:%S",
 )


routes = APIRouter()

@routes.get('/products/batch/{task_id}')
def batch_update(task_id: str):
    task_result =  AsyncResult(task_id,app=c_task)
    logging.info(f'for id {task_id} status is checked')
    return {"task_id": task_id, "status": task_result.status, "result": task_result.result} 

@routes.get('/products')
def all_products():
    logging.info('getting all data from database')
    data = collection.find().to_list()
    if not data:
        return 'no data to desplay pls add data first'
    for i in data:
        i['_id']=str(i['_id'])
    print(data)
    return data

@routes.get('/products/{product_id}',response_model=Product)
def one_product(product_id:int):
    logging.info(f'fetching data for product_id {id}')
    data = collection.find_one({'product_id':id})
    if not data:
        return {'data not found'}
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
def products_regester(data : List[Product]):
    # task = store_all_product.delay([item.dict() for item in data])
    task = store_all_product.apply_async(kwargs={'data':[item.dict() for item in data]})
    logging.info(f'for storing new data, task send to id {task.id}')
    return {"task_id": task.id}
    