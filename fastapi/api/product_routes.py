from fastapi import APIRouter, Response
from models.Product import Product
from db.products import get_products, get_product_with_id
from celery.result import AsyncResult
from utils.error_handler import NoProductFound, NoProductFoundInDB
from celery_app import app
product = APIRouter(prefix='/products')


@product.post('/batch') 
def insert_product_batch(products : list[Product]):
    
    res = app.send_task('insert_products', kwargs={'products':[product.model_dump() for product in products]},queue='product_queue')

    return {'msg':f'Insert products task started with id {res.id}'}


@product.get("/batch/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)  
    
    if task_result.ready():  
        return {"task_id": task_id, "status": "completed", "result": task_result.result}
    elif task_result.failed():  
        return {"task_id": task_id, "status": "failed"}
    elif task_result.status == 'PENDING':  
        print('Task is pending')
        return {"task_id": task_id, "status":"pending"}
    else:
        return {"task_id": task_id, "State":task_result.state, "info":task_result.info}
    


@product.get("/")
def get_products_route():
    res = get_products()
    if res is None or res == {}:
        raise NoProductFoundInDB()
    return {'products':res}
    

@product.get("/{productId}")
def get_product_with_id_route(productId:int):
    res = get_product_with_id(productId)
    if res is None or res == {}:
        raise NoProductFound(id=productId)
    return {'products':res}
    
    
