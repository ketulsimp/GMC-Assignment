from conf.celery_client import celery
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from conf.settings import settings
import time
from celery.exceptions import Ignore
# from product
from product_batch_logger.celery_logger import celery_logger


@celery.task(bind=True,name='batch_store_in_mongo')
def batch_store_in_mongo(self,docs,correlation_id):
    task_id = self.request.id.__str__()
    celery_logger.info(f"Task Started",extra={'task_id':task_id,'correlation_id':correlation_id})
    client = MongoClient(settings.mongo_uri)
    db = client["task_2_microservice"]
    batch_size = 100
    faulty_products = list()
    for i in range(0,len(docs),batch_size):
        self.update_state(state='PROGRESS',meta={'current':'current'})
        time.sleep(10) #for testing purposes only
        batch_docs = docs[i:i+batch_size]
        try:
            db.products.insert_many(batch_docs,ordered=False)
        except BulkWriteError as e:
            for error in e.details.get('writeErrors'):
                temp_doc = batch_docs[error.get('index')]
                del temp_doc['_id']
                faulty_products.append(temp_doc)
                
                
    if faulty_products:
        self.update_state(state='FAILURE',meta={'exc_type': 'FAILURE INSERTING PRODUCTS',
                                         'exc_message': 'Failed to insert these products because of similar skus, gsin or internal server error.', 'faulty_products': faulty_products})
        celery_logger.error(f"Task failed becuase of similar sku, gsin or internal server error.",extra={'correlation_id': correlation_id,'task_id':task_id})
        raise Ignore()
    else:
        self.update_state(state='SUCCESS',meta={'current':'current'})
        celery_logger.info(f"Task executed successfully.",extra={'correlation_id': correlation_id,'task_id':task_id})
