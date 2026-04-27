from fastapi import FastAPI
from task2.fastapi_service.routes.router import router
from asgi_correlation_id import CorrelationIdMiddleware

app=FastAPI()
app.include_router(router)
app.add_middleware(CorrelationIdMiddleware) 