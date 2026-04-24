from pymongo import MongoClient,ASCENDING

client=MongoClient("mongodb://localhost:27017")
db=client['productsapi']
products=db['products']

products.create_index([('sku', ASCENDING), ('product_id', ASCENDING)], unique=True)