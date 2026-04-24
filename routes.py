from fastapi import APIRouter, HTTPException
from models import Product
from typing import List
from tasks import process_products
from celery.result import AsyncResult
from celery_worker import celery
from db import products_collection

router = APIRouter()

@router.post("/products/batch")
async def add_products(products: List[Product]):
    if not products:
        raise HTTPException(status_code=400, detail="Empty list")

    data = [p.model_dump(mode="json") for p in products]
    task = process_products.apply_async(args=[data])

    return {"task_id": task.id}


@router.get("/products/batch/{task_id}")
async def get_batch_status(task_id: str):
    task = AsyncResult(task_id, app=celery)

    return {
        "task_id": task_id,
        "state": task.state,
        "meta": task.info
    }


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
        raise HTTPException(status_code=404, detail="Not found")

    product["_id"] = str(product["_id"])
    return product

