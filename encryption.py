# encryption.py
from cryptography.fernet import Fernet
import base64

def generate_key():
    """Generate a Fernet key for encryption."""
    return Fernet.generate_key()

def encrypt_code(code: str, key: bytes) -> str:
    """Encrypt the given code using the provided key."""
    fernet = Fernet(key)
    encrypted = fernet.encrypt(code.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_code(encrypted_code: str, key: bytes) -> str:
    """Decrypt the given encrypted code using the provided key."""
    fernet = Fernet(key)
    decrypted = fernet.decrypt(base64.b64decode(encrypted_code.encode()))
    return decrypted.decode()