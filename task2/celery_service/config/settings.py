import os
class Settings:
    MONGODB_URI=os.environ['MONGODB_URI']
settings=Settings()