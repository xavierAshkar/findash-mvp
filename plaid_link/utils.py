"""
plaid_link/utils.py

Contains utilities for:
- Encrypting/decrypting access tokens
- Initializing Plaid client
"""

from decouple import config
from cryptography.fernet import Fernet

from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.api import plaid_api

# Initialize Fernet encryption with key from .env
try:
    fernet = Fernet(config("FERNET_KEY"))
except Exception as e:
    raise RuntimeError("Invalid or missing FERNET_KEY in environment.") from e

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

def get_plaid_client():
    configuration = Configuration(
        host="https://sandbox.plaid.com",
        api_key={
            "clientId": config("PLAID_CLIENT_ID"),
            "secret": config("PLAID_SECRET"),
        }
    )
    return plaid_api.PlaidApi(ApiClient(configuration))