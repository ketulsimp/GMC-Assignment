from pymongo.errors import PyMongoError
from app.log.logger import logger

class TokenNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class DatabaseError(Exception):
    pass

class InternalServerError(Exception):
    pass

async def global_error_handler():
    try:
        yield 
    except PyMongoError:
        logger.exception("Database Error")
        raise DatabaseError
    except Exception:
        logger.exception("Internal Server Error")
        raise InternalServerError