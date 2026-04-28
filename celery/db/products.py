from db.get_client import db

def insert_product(product,logger):
    logger.info({"message":f"Inserting product {product} into the database"})

    res = db.products.insert_one(product)
    logger.info({"message":f"Inserted product {product} into the database"})
    
    return res

