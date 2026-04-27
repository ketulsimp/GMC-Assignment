from pymongo.errors import BulkWriteError, PyMongoError
from pymongo import MongoClient
import time
from app.config.settings import settings
from celery import Celery
from app.config.settings import settings
from celery.exceptions import Ignore
# from app.logs.logger import logger
from app.logs.logger import worker_logger

celery = Celery(
    "tasks",
    broker=settings.broker_uri,
    backend=settings.backend_uri
)

celery

@celery.task(bind=True)
def batch_store_in_mongo(self,docs):
    worker_logger.info(f"TaskID: {self.request.id.__str__()} started.")
    client = MongoClient(settings.mongo_uri)
    db = client["task_2"]
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
        raise Ignore()
    else:
        self.update_state(state='SUCCESS',meta={'current':'current'})
        worker_logger.info(f"TaskID: {self.request.id.__str__()} executed successfully.")
