from conf.celery_client import celery
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from logs.logger import worker_logger, celery_logger
from conf.settings import settings
import time
from celery.exceptions import Ignore



@celery.task(bind=True,name='batch_store_in_mongo')
def batch_store_in_mongo(self,docs):
    worker_logger.info(f"TaskID: {self.request.id.__str__()} started.")
    client = MongoClient(settings.mongo_uri)
    db = client["task_2_microservice"]
    batch_size = 100
    faulty_products = list()
    for i in range(0,len(docs),batch_size):
        self.update_state(state='PROGRESS',meta={'current':'current'})
        time.sleep(10)
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
        worker_logger.error(f"TaskID: {self.request.id.__str__()} failed becuase of similar sku, gsin or internal server error.")
        celery_logger.error(f"TaskID: {self.request.id.__str__()} failed becuase of similar sku, gsin or internal server error.")
        raise Ignore()
    else:
        self.update_state(state='SUCCESS',meta={'current':'current'})
        celery_logger.info(f"TaskID: {self.request.id.__str__()} executed successfully.")
