from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    mongo_uri:str = os.environ.get('MONGO_URI',"mongodb")
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    secret_key: str = os.environ.get('SECRET_KEY')
    session_secret_key = os.environ.get('SESSION_SECRET_KEY')
    
settings = Settings()