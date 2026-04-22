from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class MerchantAccounts(BaseModel):
    mechant_name:str | None = None
    user_id: str | None = None
    google_id: str | None = None


