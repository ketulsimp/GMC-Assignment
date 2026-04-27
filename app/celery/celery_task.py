from app.celery.celery_app import c_task
# from celery.exceptions import Ignore
from app.db import collection
from pymongo.errors import DuplicateKeyError
# from app.logger import log
# import logging

# logging.basicConfig(
#     level=logging.INFO,
#      filename="app.log",
#      encoding="utf-8",
#      filemode="a",
#      format="{asctime} - {levelname} - {message}",
#      style="{",
#      datefmt="%Y-%m-%d %H:%M:%S",
#  )


@c_task.task(bind=True)
def store_all_product(self, data: list):
    total = len(data)
    results = []

    for i, item in enumerate(data):
        try:
            collection.insert_one(item)
            # print(i)
            results.append({
                "product_id": item["product_id"],
                "status": "success"
            })

        except DuplicateKeyError:
            results.append({
                "product_id": item["product_id"],
                "status": "failed",
                "reason": "duplicate"
            })

        except Exception as e:
            results.append({
                "product_id": item["product_id"],
                "status": "failed",
                "reason": str(e)
            })

        # progress update
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": total,
                "results": results
            }
        )

    # log("Batch processing completed")

    return {
        "status": "completed",
        "total": total,
        "results": results
    }
    
    
    

# @c_task.task(bind=True)
# def store_all_product(self,data:list):
#     duplicate = []
#     insert_data = []
    
#     # logging.info('data is being validated')
#     for i in data:
#         p_id = collection.find_one({'product_id':i['product_id']})
#         sku = collection.find_one({'sku':i['sku']})
#         gtin = collection.find_one({'gtin':i['gtin']})
#         self.update_state(state='validatin data', meta={'msg':'data is being validated before entering database'})
#         if p_id:
#             duplicate.append(f'{p_id} product id is already regestered')
#             continue
#         if sku:
#             duplicate.append(f'{sku} sku is already regestered')
#             continue
#         if gtin:
#             duplicate.append(f'{gtin} gtin is already regestered')
#             continue

#         insert_data.append(i)
        
#     for i in data:
#         try:
#             collection.insert_one(i)
#         except DuplicateKeyError:
#             duplicate.append(...)
        
#     for i in range (len(insert_data)):
#         for j in range(i,len(insert_data)-1):
#             if insert_data[i]['product_id'] == insert_data[j]['product_id']:
#                 duplicate.append(f'product id {insert_data[j]["product_id"]} is inserted twice')
#                 insert_data.pop(j)
#                 continue
#             if insert_data[i]['sku'] == insert_data[j]['sku']:
#                 duplicate.append(f'sku {insert_data[j]["sku"]} is inserted twice')
#                 insert_data.pop(j)
#                 continue
#             if insert_data[i]['gtin'] == insert_data[j]['gtin' ]:
#                 duplicate.append(f'gtin {insert_data[j]["gtin"]} is inserted twice')
#                 insert_data.pop(j)
#                 continue
    
    
#     #data insertion
#     print(insert_data)
    
#     if not insert_data:
#         return 'no data to add all data is already regestered'
    
#     if duplicate:
#         collection.insert_many(insert_data)
#         self.update_state(state='parsial success', meta={'msg':'some data found duplicate and other non duplicate data inserted','data':duplicate})
#         raise Ignore('there were some duplicate in the data')
        
#     collection.insert_many(insert_data)
#     self.update_state(state='inserting data', meta={'msg':'data is being inserted to the database'})
    
#     return duplicate
    
    
 