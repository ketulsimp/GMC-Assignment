from pydantic import BaseModel

class RefreshRequest(BaseModel):
    refreshToken: str 

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str