from fastapi.responses import JSONResponse
from fastapi import Request


class NoProductFound(Exception):
    def __init__(self, id: str):
        self.id = id


async def no_productID_found_exception_handler(req:Request,exc: NoProductFound):
    return JSONResponse(
        status_code=404,
        content={"message": f"No Product with {exc.id} Found"},
    )


class NoProductFoundInDB(Exception):
    pass

async def no_product_found_in_db_exception_handler(req:Request,exc: NoProductFound):
    return JSONResponse(
        status_code=404,
        content={"message": f"No Product with id {exc.id} Found"},
    )


