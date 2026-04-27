from celery_app import c_task
from db import collection
from pymongo.errors import DuplicateKeyError



@c_task.task(bind=True)
def store_all_product(self, data: list):
    total = len(data)
    inserted = 0 
    results = []

    with open('logs.log','a') as f:
        f.write('\nadding data to database')
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
            
            with open('logs.log','a') as f:
                f.write(f'\ndata duplicate at {duplicate_field} - {duplicate_value}')

            results.append({
                "product_id": item["product_id"],
                "status": "failed",
                "reason": f"Duplicate {duplicate_field}",
                "field": duplicate_field,
                "value": duplicate_value
            })

        except Exception as e:
            with open('logs.log','a') as f:
                f.write('\nerror ',e)
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
        
    with open('logs.log','a') as f:
                f.write('\ndata insertion performed successfully')

    return {
        "status": "completed",
        "total": total,
        "inserted_data": inserted,
        "not_inserted_data": total-inserted,
        "results": results
    }


    