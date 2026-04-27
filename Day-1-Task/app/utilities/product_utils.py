from app.models.product_model import Product
from typing import List
from collections import defaultdict

def check_similarity(products: List[Product]):
    visited_sku = defaultdict(int)
    visited_gsin = defaultdict(int)
    for product in products:
        visited_sku[product.sku] += 1
        visited_gsin[product.gsin] += 1
    similar_skus = [k for k,v in visited_sku.items() if v>1]
    similar_gsin = [k for k,v in visited_gsin.items() if v>1]
    return {'Duplicate SKU': similar_skus, 'Duplicate GSIN': similar_gsin} if similar_skus or similar_gsin else None

def serialize(products: List[Product]):
    return [product.model_dump() for product in products]