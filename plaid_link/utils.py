from decouple import config
from cryptography.fernet import Fernet

fernet = Fernet(config("FERNET_KEY"))

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
