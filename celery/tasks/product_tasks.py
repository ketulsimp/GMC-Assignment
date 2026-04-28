from celery_app import app
from db.products import insert_product
from pymongo.errors import DuplicateKeyError
import asyncio, time
from logger.main import mylogger

logger = mylogger()


@app.task(name="insert_products",bind=True,default_retry_delay = 3,acks_late=True)
def insert_batch_products(self,products: list[dict],errors:list = [], inserted_ids:list = [], rejected_ids=[]):

    try: 
        for product in products:
            self.update_state(
                state='PROGRESS',
                meta={'current': product.get('id'), 'total': len(products), 'status': 'Inserting Product'}
            )
            logger.info({"message":f"Task in progress current product ID : {product.get('id')} / total {len(products)}"})
            res = insert_product(product=product,logger=logger)
            inserted_ids.append(product.get('id'))
        return {"Total Products Inserted":len(inserted_ids),"Errors in Inserting ":errors, "Inserted Product IDs":inserted_ids,"Rejected Product IDs":rejected_ids}
    
    except DuplicateKeyError as e:
        errors.append(str(e))
        rejected_ids.append(product.get('id'))
        self.update_state(
                state='PROGRESS',
                meta={'current': product.get('id'), 'total': len(products), 'status': 'Inserting Product'}
            )
        logger.error({"message":f"Error in inserting product with id : {product.get('id')} , error : {str(e)}"})
        time.sleep(10)
        l = len(inserted_ids)
        if len(products[l+1:])==0:
            logger.error({"message":f"Task Completed Sending the Response Total Products Inserted : {len(inserted_ids)}  Errors in Inserting : {errors} Inserted Product IDs : {inserted_ids} Rejected Product IDs: {rejected_ids}"})
            return {"Total Products Inserted":len(inserted_ids),"Errors in Inserting ":errors, "Inserted Product IDs":inserted_ids, "Rejected Product IDs: ":rejected_ids}
        raise self.retry(args=(),kwargs={'products':products[l+1:],'errors':errors,'inserted_ids':inserted_ids,'rejected_ids':rejected_ids})

    except Exception as e:
        logger.error('Unexpeted Error while inserting product : ',str(e))
        raise e
    
