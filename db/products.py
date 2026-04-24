from db.get_client import db
from models.Product import Product

def insert_product(product):
    res = db.products.insert_one(product)
    return res

def get_products():
    res = db.products.find({},{'_id':0})
    print(res)
    print(type(res))
    return list(res)

def get_product_with_id(id:int):
    res = db.products.find_one({'id':id},{'_id':0})
    return res



