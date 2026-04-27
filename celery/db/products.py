from db.get_client import db
from logger import logger

def insert_product(product):
    logger.info(f"Inserting product {product} into the database")

    res = db.products.insert_one(product)
    logger.info(f"Inserted product {product} into the database")
    
    return res

