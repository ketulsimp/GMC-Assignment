from fastapi import APIRouter
from models.Product import Product
from tasks.product_tasks import insert_batch_products
from celery.result import AsyncResult
from db.products import get_products, get_product_with_id
from fastapi.exceptions import HTTPException

product = APIRouter(prefix='/products')


@product.post('/batch') 
def insert_product_batch(products : list[Product]):
    res = insert_batch_products.apply_async(args=(products,[],[] ,[])) 

    return {'msg':f'Insert products task started with id {res.id}'}


@product.get("/batch/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)  
    
    if task_result.ready():  
        return {"task_id": task_id, "status": "completed", "result": task_result.result}
    elif task_result.failed():  
        return {"task_id": task_id, "status": "failed"}
    else:  
        print(task_result.state)
        
        return {"task_id": task_id, "status": "in progress"}
    


@product.get("/")
def get_products_route():
    try:
        res = get_products()
        return {'products':res}
    except Exception as e:
        return {'error':str(e)}
    

@product.get("/{productId}")
def get_product_with_id_route(productId:int):
    try:
        res = get_product_with_id(productId)
        if res == {}:
            return HTTPException(404,f'Product with ID {productId} not found ')
        return {'products':res}
    except Exception as e:
        return {'error':str(e)}
    
