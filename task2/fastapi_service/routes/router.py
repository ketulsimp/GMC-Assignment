from fastapi import APIRouter, HTTPException
from task2.fastapi_service.schemas.schema import Products
from typing import List
from celery import Celery
from celery.result import AsyncResult
from task2.fastapi_service.models.db_model import products,db
from typing import List
from task2.fastapi_service.config.logging import logger
import os
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()
celery=Celery("worker",broker=os.environ['REDIS_URI'],backend=os.environ['REDIS_URI'])

@router.post("/products/batch")
async def add_products(products_input: List[dict]):
    valid_products = []
    error_message={}
    visited=[]
    for item in products_input: 
        try:
            product = Products(**item)
            if item['product_id'] not in visited and not products.find_one({'product_id':item['product_id']}):
                valid_products.append(product)
                visited.append(item['product_id'])
            # error_message.update({'item': item,'error': 'Product already exist'})
        except Exception as e:
            logger.error(e)
            error_message.update({"item": item, "error": str(e)})
    if not valid_products:
        raise HTTPException(status_code=400, detail={"message": "No valid products to insert", "errors": error_message})

    data = [p.model_dump(mode="json") for p in valid_products]
    task = celery.send_task(name='worker.process_products',args=[data])
    return {"task_id": task.id, "accepted_count": len(valid_products),"failed_count": len(error_message),"errors":error_message}


# @router.post("/products/batch")
# async def add_products(products:list[Products]):
#     try:
#         task=process_products.apply_async(args=[products])
#         return task.id
#     except Exception as e:
#         raise Exception(e)

@router.get("/products/batch/{task_id}")
async def get_status(task_id: str):
    task = AsyncResult(task_id, app=celery)
    return {"task_id": task_id,"state": task.state,"meta": task.info}


@router.get("/products")
async def get_products():
    query= db.products.find()
    products_list = []
    for p in query:
        p["_id"] = str(p["_id"])
        products_list.append(p)
    return products_list


@router.get("/products/{product_id}")
async def product_by_id(product_id: int):
    product = products.find_one({"product_id": product_id},{"_id":0})
    if not product:
        logger.error(f"Product with id : {product_id} found")
        raise HTTPException(status_code=404, detail="Not found")
    logger.info(f"Product with id : {product_id} found")
    return product
