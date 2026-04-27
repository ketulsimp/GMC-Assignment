from celery import Celery
from task2.celery_service.models.db_model import products
from pymongo.errors import DuplicateKeyError
from task2.celery_service.config.logging import logger
import os
from dotenv import load_dotenv


load_dotenv()
celery = Celery("worker",broker=os.environ['REDIS_URI'],backend=os.environ['REDIS_URI'])

@celery.task(bind=True,name='worker.process_products')
def process_products(self,products_data):
    total_products = len(products_data)
    inserted_count=0
    failed=0
    errors=[]

    for i,product in enumerate(products_data):
        try:
            products.insert_one(product)  
            inserted_count += 1
            logger.info(f'Product inserted {product}')
        except DuplicateKeyError as e:
            failed += 1
            errors.append({"product_id":product['product_id'], "error": str(e)})
            logger.error(e)
            
        except Exception as e:
            failed += 1
            errors.append({"error": str(e)})
            logger.error(e)

        self.update_state(state="PROGRESS",meta={"Total": total_products,"Processed": i + 1,"Success": inserted_count,"Failed": failed})

    return {"Total": total_products,"Success": inserted_count,"Failed": failed,"Errors": errors}

