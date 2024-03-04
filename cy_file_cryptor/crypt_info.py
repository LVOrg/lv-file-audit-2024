import base64
import gc
import json
import uuid

from cryptography.fernet import Fernet


def write_dict(data: dict, file_path):
    key = uuid.UUID("14b9fdee-cb1c-4180-b9c3-78e26b44e77b").bytes + \
          uuid.UUID("869edadd-35df-4615-9de3-95e98835d3ab").bytes
    bas64_key=  base64.b64encode(key)

    fernet = Fernet(bas64_key)
    txt_json = json.dumps(data)
    encrypted_text = fernet.encrypt(txt_json.encode('utf8'))
    with open(file_path, "wb") as f:
        f.write(encrypted_text)


def read_dict(file_path) -> dict:
    key = uuid.UUID("14b9fdee-cb1c-4180-b9c3-78e26b44e77b").bytes + \
          uuid.UUID("869edadd-35df-4615-9de3-95e98835d3ab").bytes
    bas64_key = base64.b64encode(key)
    fernet = Fernet(bas64_key)
    with open(file_path, "rb") as f:
        data = f.read()
        txt_json = fernet.decrypt(data).decode('utf8')
        ret = json.loads(txt_json)
        del txt_json
        del data
        gc.collect()
        return ret
