from app.config.db import get_sync_db
from typing import List
from pymongo.errors import BulkWriteError
from pymongo import MongoClient
import time
from app.config.settings import settings
from celery import Celery
from app.config.settings import settings
from celery.exceptions import Ignore

celery = Celery(
    "tasks",
    broker=settings.broker_uri,
    backend=settings.backend_uri
)

@celery.task(bind=True)
def batch_store_in_mongo(self,docs):
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
        self.update_state(state='FAILURE',meta={'exc_type': 'Similar SKU or GSIN already Exist',
                                         'exc_message': 'Some Fields are already existing', 'faulty_products': faulty_products})
        raise Ignore()
    else:
        self.update_state(state='SUCCESS',meta={'current':'current'})