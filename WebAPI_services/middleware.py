from fastapi import Request
from fastapi.responses import JSONResponse
import uuid
from workerlogger import get_logger
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

logger = get_logger(service_name="web-api-service")


async def logging_middleware(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    extra = {"correlation_id": correlation_id}

    logger.info(f"Request: {request.method} {request.url}", extra=extra)

    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}", extra=extra)   
        return response

    except PyMongoError as e:
        logger.error(f"MongoDB error: {str(e)}", extra=extra)
        return JSONResponse(status_code=503, content={"detail": "Database unavailable"})

    except RedisError as e:
        logger.error(f"Redis error: {str(e)}", extra=extra)
        return JSONResponse(status_code=503, content={"detail": "Task queue unavailable"})

    except Exception as e:
        logger.error(f"Error: {str(e)}", extra=extra)
        raise e
