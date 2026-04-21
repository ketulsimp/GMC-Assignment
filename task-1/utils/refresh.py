import httpx
import os
from database.db import oauth_tokens

TOKEN_REQUEST_URI="https://oauth2.googleapis.com/token"
async def refresh_access_token(email:str,code:str):
    async with httpx.AsyncClient() as client:
        token_response=await client.post(TOKEN_REQUEST_URI,data={
            'code':code,
            'client_id': os.environ['GOOGLE_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
            'refresh_token':'refresh_token',
            'grant_type': 'authorization_code'
        })
        token=token_response.json()
        await oauth_tokens.update_one({'email':email},{"$set":{'access_token':token}})