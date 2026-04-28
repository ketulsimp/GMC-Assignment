

from fastapi import FastAPI
from routes import router
from db import create_db_indexes
from middleware import logging_middleware
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from workerlogger import get_logger


app = FastAPI(title="Web API Service")


app = FastAPI()

app.middleware("http")(logging_middleware)

@app.on_event("startup")
async def startup_event():
    await create_db_indexes()

logger = get_logger(service_name= "web-api-service")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = str(exc.errors())
    logger.warning(
        f"Validation failed: {error_messages}",
        extra={"correlation_id": "N/A"}
    )
    return JSONResponse(status_code=422, content={"detail": error_messages})


app.include_router(router)