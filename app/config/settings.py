from dotenv import load_dotenv
import os 

load_dotenv()

class Settings():
    broker_uri: str = os.environ.get("BROKER_URI")
    backend_uri: str = os.environ.get("BACKEND_URI")
    mongo_uri: str = os.environ.get("MONGO_URI")
    
settings = Settings()