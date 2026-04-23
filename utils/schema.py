from pydantic import BaseModel

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str