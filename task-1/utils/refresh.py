import httpx
import os
from datetime import datetime, timedelta
from database.db import oauth_tokens

TOKEN_REQUEST_URI = "https://oauth2.googleapis.com/token"

async def refresh_access_token(email: str, refresh_token: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(TOKEN_REQUEST_URI, data={
            'client_id': os.environ['GOOGLE_CLIENT_ID'],
            'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        })
        token=token_response.json()
        access_token=token['access_token']

        await oauth_tokens.update_one({'email': email},{"$set": {'access_token': access_token,'expiry': datetime.now() + timedelta(seconds=token['expires_in'])}})
        return access_token