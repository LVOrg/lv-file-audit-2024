import base64
import gc
import json
import uuid

from cryptography.fernet import Fernet


def write_dict(data: dict, file_path,original_open):
    key = uuid.UUID("14b9fdee-cb1c-4180-b9c3-78e26b44e77b").bytes + \
          uuid.UUID("869edadd-35df-4615-9de3-95e98835d3ab").bytes
    bas64_key=  base64.b64encode(key)

    fernet = Fernet(bas64_key)
    txt_json = json.dumps(data)
    encrypted_text = fernet.encrypt(txt_json.encode('utf8'))
    with original_open(file_path, "wb") as f:
        f.write(encrypted_text)


def read_dict(file_path,original_open) -> dict:
    key = uuid.UUID("14b9fdee-cb1c-4180-b9c3-78e26b44e77b").bytes + \
          uuid.UUID("869edadd-35df-4615-9de3-95e98835d3ab").bytes
    bas64_key = base64.b64encode(key)
    fernet = Fernet(bas64_key)
    with original_open(file_path, "rb") as f:
        data = f.read()
        txt_json = fernet.decrypt(data).decode('utf8')
        ret = json.loads(txt_json)
        if ret.get('header'):
            from cy_file_cryptor import encrypting
            ret['header'] = base64.b64decode(ret['header'])
            ret['header'] = next(encrypting.decrypt_content(
                data_encrypt=ret['header'],
                chunk_size=len(ret['header']),
                rota=1,
                first_data=ret['header-first']
            ))

        if ret.get('footer'):
            from cy_file_cryptor import encrypting
            ret['footer'] = base64.b64decode(ret['footer'])
            ret['footer'] = next(encrypting.decrypt_content(
                data_encrypt=ret['footer'],
                chunk_size=len(ret['footer']),
                rota=1,
                first_data=ret['footer-first']
            ))
        del txt_json
        del data
        gc.collect()
        return ret
