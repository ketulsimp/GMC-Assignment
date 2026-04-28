from fastapi import FastAPI
from api.product_routes import product
from utils.middleware import LoggingMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from utils.error_handler import NoProductFound, no_product_found_in_db_exception_handler, no_productID_found_exception_handler, NoProductFoundInDB

app = FastAPI()



app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.add_exception_handler(NoProductFound,no_productID_found_exception_handler)
app.add_exception_handler(NoProductFoundInDB,no_product_found_in_db_exception_handler)


app.include_router(product)

@app.get('/')
def index():
    return {'msg':'index route running'}