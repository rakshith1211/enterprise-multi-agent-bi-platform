import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Development/Testing fallback encryption key
DEFAULT_DEV_KEY = "k1_M2v_hP3v4lS5k6t7u8v9w0x1y2z3a4b5c6d7e8f8="

def get_encryption_key() -> bytes:
    key_str = os.getenv("ENCRYPTION_KEY")
    if not key_str:
        logger.warning("ENCRYPTION_KEY environment variable is not set. Falling back to default development key.")
        return DEFAULT_DEV_KEY.encode()
    try:
        key = key_str.encode()
        # Verify validity
        Fernet(key)
        return key
    except Exception as exc:
        logger.error(f"Provided ENCRYPTION_KEY is invalid: {exc}. Falling back to default development key.")
        return DEFAULT_DEV_KEY.encode()

class CredentialEncryptor:
    def __init__(self):
        self.fernet = Fernet(get_encryption_key())

    def encrypt(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        return self.fernet.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        if not cipher_text:
            return ""
        try:
            return self.fernet.decrypt(cipher_text.encode()).decode()
        except Exception as exc:
            logger.error(f"Decryption failed: {exc}")
            raise ValueError("Decryption of database credentials failed. Check your ENCRYPTION_KEY.")

encryptor = CredentialEncryptor()
