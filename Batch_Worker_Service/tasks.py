from celery_app import celery_app
from pymongo.errors import DuplicateKeyError
from database import products_collection_sync
from workerlogger import get_logger

logger = get_logger(service_name="worker-service")


@celery_app.task(bind=True, name="tasks.process_products")
def process_products(self, products):
    logger.info(f"Received batch of {len(products)} products")
    total = len(products)
    success = 0
    failed = 0
    errors = []

    for i, product in enumerate(products):
        product_id = product.get("product_id", "unknown")
        try:
            products_collection_sync.insert_one(product)
            success += 1
        except DuplicateKeyError as e:
            failed += 1
            error_msg = str(e)
            if "sku" in error_msg:
                reason = f"Duplicate SKU: {product.get('sku')}"
            elif "product_id" in error_msg:
                reason = f"Duplicate product_id: {product_id}"
            else:
                reason = "Duplicate key"
            errors.append({
                "product_id": product_id,
                "sku": product.get("sku"),
                "error": reason,
            })
            logger.error(f"{reason} - product_id={product_id} sku={product.get('sku')}")

        self.update_state(
            state="PROGRESS",
            meta={
                "total": total,
                "processed": i + 1,
                "success": success,
                "failed": failed,
            },
        )

    return {"total": total, "success": success, "failed": failed, "errors": errors}