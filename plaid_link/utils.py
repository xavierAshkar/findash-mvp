from decouple import config
from cryptography.fernet import Fernet

# Initialize Fernet encryption with key from .env
fernet = Fernet(config("FERNET_KEY"))


def encrypt_token(token: str) -> str:
    """
    Encrypt a plaintext token using Fernet symmetric encryption.
    Returns the encrypted string (base64-encoded).
    """
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    """
    Decrypt an encrypted token back to plaintext.
    Assumes the token was previously encrypted with encrypt_token.
    """
    return fernet.decrypt(token.encode()).decode()
