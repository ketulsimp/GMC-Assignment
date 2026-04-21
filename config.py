
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
FERNET_KEY = os.getenv("FERNET_KEY")
