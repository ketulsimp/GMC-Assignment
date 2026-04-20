from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    mongo_uri:str = "mongodb://localhost:27017/"
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    secret_key: str = "This_is_secret_key_for_jwt_session_authentication"
    
settings = Settings()