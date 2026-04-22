from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
# from cryptography.fernet import Fernet

# key = Fernet.generate_key()
# crypt = Fernet(key=key)



DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String,unique=True)
    
class Token(Base):
    __tablename__ = "oauth_tokens"
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, index=True)
    refresh_token = Column(String)
    session_id = Column(String)
    expires_at = Column(DateTime)
    user_email = Column(String,unique=True)
    
    
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# def crypt_token(token):
#     token = bytes(token,'utf-8')
#     data = crypt.encrypt(token).decode()
#     return data

# def decrypt_token(token):
#     token = bytes(token,'utf-8')
#     data = crypt.decrypt(token).decode()
#     return data