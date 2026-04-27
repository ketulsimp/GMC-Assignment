from app.config.db import get_db

async def fetch_products():
    _db = await get_db()
    products = []
    async for product in _db.products.find({},{'_id':0}):
        products.append(product)
    return products

async def fetch_product_by_id(id: str):
    _db = await get_db()
    return await _db.products.find_one({'sku':id})