from fastapi import FastAPI,HTTPException,Request
from asgi_correlation_id import CorrelationIdMiddleware,correlation_id
from fastapi.exception_handlers import http_exception_handler
from app.db import collection
from app.service.routes import routes
from fastapi.responses import JSONResponse


app = FastAPI()
app.add_middleware(CorrelationIdMiddleware,
                   header_name='X-Request-ID',
                    update_request_header=True,)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            'Internal server error',
            headers={'X-Request-ID': correlation_id.get() or ""}
        ))

app.include_router(routes)

@app.on_event("startup")
def startup_event():
    collection.create_index([("sku", 1)], unique=True)
    collection.create_index([('gtin',1)],unique=True)
    collection.create_index([('product_id',1)],unique=True)

@app.get("/")
def home():
    return {'welcome to batch product regestration'}