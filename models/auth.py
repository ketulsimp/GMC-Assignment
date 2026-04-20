from pydantic import BaseModel


class User(BaseModel):
    email:str | None = None
    password: str | None = None


class google_accounts(BaseModel):
    email:str | None = None
    name:str | None = None


class OAuthToken(BaseModel):
    access_token: str
    refresh_token: str
    expiry: str
    user_id: str


