from fastapi import FastAPI
from api.product_routes import product
from middleware import LoggingMiddleware



app = FastAPI()

app.add_middleware(LoggingMiddleware)

app.include_router(product)

@app.get('/')
def index():
    return {'msg':'index route running'}