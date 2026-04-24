from celery_app import app
from models.Product import Product
from db.products import insert_product
from pymongo.errors import DuplicateKeyError
import asyncio, time
from logger import logger


@app.task(bind=True,default_retry_delay = 3,acks_late=True)
def insert_batch_products(self,products: list[Product],errors:list = [], inserted_ids:list = [], rejected_ids=[]):

    try: 
        for product in products:
            self.update_state(
                state='PROGRESS',
                meta={'current': product.id, 'total': len(products), 'status': 'Inserting Product'}
            )
            logger.info({"message":f"Task in progress current product ID : {product.id} / total {len(products)}"})
            res = insert_product(product=product.model_dump())
            inserted_ids.append(product.id)
        return {"Total Products Inserted":len(inserted_ids),"Errors in Inserting ":errors, "Inserted Product IDs":inserted_ids}
    
    except DuplicateKeyError as e:
        errors.append(str(e))
        rejected_ids.append(product.id)
        self.update_state(
                state='PROGRESS',
                meta={'current': product.id, 'total': len(products), 'status': 'Inserting Product'}
            )
        logger.error({"message":f"Error in inserting product with id : {product.id} , error : {str(e)}"})
            
        time.sleep(10)
        l = len(inserted_ids)
        if len(products[l+1:])==0:
            return errors,inserted_ids, rejected_ids
        raise self.retry(args=(),kwargs={'products':products[l+1:],'errors':errors,'inserted_ids':inserted_ids,'rejected_ids':rejected_ids})
