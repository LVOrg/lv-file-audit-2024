import base64
from cryptography.fernet import Fernet
import uuid


def encode(data: bytes) -> bytes:
    key_data = uuid.UUID("f61bd50e-92ad-4f06-84cd-060fedbc24da").bytes
    key_data += uuid.UUID("f5597812-d3a9-497e-8aba-2065c42cae9f").bytes
    key = base64.b64encode(key_data)
    fernet = Fernet(key)
    # Encrypt the message
    encrypted_text = fernet.encrypt(data)
    return encrypted_text


def decode(data: bytes) -> bytes:
    key_data = uuid.UUID("f61bd50e-92ad-4f06-84cd-060fedbc24da").bytes
    key_data += uuid.UUID("f5597812-d3a9-497e-8aba-2065c42cae9f").bytes
    key = base64.b64encode(key_data)
    fernet = Fernet(key)
    encrypted_text = fernet.decrypt(data)
    return encrypted_text
