
from celery_worker import celery
from pymongo.errors import DuplicateKeyError
from sync_database import sync_database,products_collection_sync
@celery.task(bind=True)
def process_products(self, products):
    total = len(products)
    success = 0
    failed = 0
    errors = []

    for i, product in enumerate(products):
        try:
            products_collection_sync.insert_one(product)  
            success += 1
        except DuplicateKeyError as e:
            failed += 1
            errors.append({"sku": product.get("sku"), "error": str(e)})
        except Exception as e:
            failed += 1
            errors.append({"error": str(e)})

        self.update_state(
            state="PROGRESS",
            meta={
                "total": total,
                "processed": i + 1,
                "success": success,
                "failed": failed,
            }
        )

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "errors": errors
    }
