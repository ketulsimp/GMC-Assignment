from fastapi import FastAPI,Request,Response
from starlette.middleware.base import BaseHTTPMiddleware
from db import collection
from app.routes import routes
import uuid


def generate_correlation_id():
    return str(uuid.uuid4())

app = FastAPI()

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    
app.add_middleware(CorrelationIDMiddleware)

app.include_router(routes)

@app.on_event("startup")
def startup_event():
    collection.create_index([("sku", 1)], unique=True)
    collection.create_index([('gtin',1)],unique=True)
    collection.create_index([('product_id',1)],unique=True)

@app.get("/")
def home():
    return {'welcome to batch product regestration'}