from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class User(BaseModel):
    email:str | None = None
    password: str | None = None
    name: str | None = None


class Google_Accounts(BaseModel):
    email:str | None = None
    name:str | None = None
    picture:str | None = None
    lastLogin: datetime | None = Field(default_factory=lambda: datetime.now())


class OAuthToken(BaseModel):
    access_token: str
    refresh_token: str
    
    expiry: datetime = datetime.now() + timedelta(minutes=59,seconds=59)
    user_id: str


