
from cryptography.fernet import Fernet
from config import FERNET_KEY

fernet = Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
