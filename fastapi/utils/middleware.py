from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import iterate_in_threadpool
from fastapi import Request
from logger.main import mylogger 
logger = mylogger()



class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        method = request.method
        url = request.url.path

        logger.info({"message",f"Request: {method} {url} from {client_ip}"})

        response = await call_next(request)

        res_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(res_body))
        res_body = res_body[0].decode()

        status_code = response.status_code
        if status_code >= 400 and status_code <= 500:
            logger.error({"message":f"Error in calling {method} {url} returned {status_code} to {client_ip} {res_body}"})

        logger.info({"message":f"Response: {method} {url} returned {status_code} to {client_ip} {res_body}"})

        return response
    
