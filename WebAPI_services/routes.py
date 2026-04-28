from fastapi import APIRouter, HTTPException
from models import Product
from typing import List
from celery import Celery
from celery.result import AsyncResult
from db import products_collection
from dotenv import load_dotenv
import os
from workerlogger import get_logger
load_dotenv()

router = APIRouter()

celery_web = Celery(
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)
logger= get_logger(service_name= "web-api-service")


@router.post("/products/batch")
async def add_products(products: List[Product]):
    if not products:
        raise HTTPException(status_code=400, detail="Empty list")
    data = [p.model_dump(mode="json") for p in products]
    task = celery_web.send_task("tasks.process_products", args=[data])
    return {"task_id": task.id}


@router.get("/products/batch/{task_id}")
async def get_batch_status(task_id: str):
    task = AsyncResult(task_id, app=celery_web)
    if task.state == "PENDING" and task.info is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "state": task.state, "meta": task.info}


@router.get("/products")
async def get_all_products():
    products = []
    async for p in products_collection.find():
        p["_id"] = str(p["_id"])
        products.append(p)
    return products


@router.get("/products/by-product-id/{product_id}")
async def get_product_by_product_id(product_id: int):
    product = await products_collection.find_one({"product_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    product["_id"] = str(product["_id"])
    return product