from celery_app import c_task
from db import collection
from pymongo.errors import DuplicateKeyError
from log import get_logger

logging = get_logger()


@c_task.task(bind=True)
def store_all_product(self, data: list,correlation_id=None):
    total = len(data)
    inserted = 0 
    results = []

    logging.info('adding data to database',extra={"correlation_id": correlation_id})
    for i, item in enumerate(data):
        try:
            collection.insert_one(item)
            inserted +=1

        except DuplicateKeyError as e:
            error_details = e.details

            key_pattern = error_details.get("keyPattern")
            key_value = error_details.get("keyValue")

            duplicate_field = list(key_pattern.keys())[0] 
            duplicate_value = list(key_value.values())[0]
            
            logging.warn(f'data duplicate at {duplicate_field} - {duplicate_value}',extra={'correlation_id':correlation_id})

            results.append({
                "product_id": item["product_id"],
                "status": "failed",
                "reason": f"Duplicate {duplicate_field}",
                "field": duplicate_field,
                "value": duplicate_value
            })

        except Exception as e:
            logging.info('error in adding data',extra={'correlation_id':correlation_id})
            results.append({
                "product_id": item["product_id"],
                "status": "failed",
                "reason": str(e)
            })

        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": total,
                "results": results
            }
        )
        
    logging.info('data inserted successfullly',extra={'correlation_id':correlation_id})

    return {
        "status": "completed",
        "total": total,
        "inserted_data": inserted,
        "not_inserted_data": total-inserted,
        "results": results
    }


    