from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class MerchantAccount(BaseModel):
    name: str | None = None
    merchant_name:str | None = None
    accountId: str | None = None

