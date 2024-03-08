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
    tem_header = None
    tem_footer = None
    data['header'] = data.get('header', bytes([]))
    data['footer'] = data.get('footer', bytes([]))
    if isinstance(data['header'],bytes):
        tem_header = data['header']
        data['header'] = base64.b64encode(tem_header).decode("utf-8")
    if isinstance(data['footer'],bytes):
        tem_footer = data['footer']
        data['footer'] = base64.b64encode(tem_footer).decode("utf-8")

    txt_json = json.dumps(data)
    encrypted_text = fernet.encrypt(txt_json.encode('utf8'))
    with original_open(file_path, "wb") as f:
        f.write(encrypted_text)
    if tem_header:
        data['header'] = tem_footer
    if tem_footer:
        data['footer'] = tem_footer

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
        if ret.get('footer'):
            from cy_file_cryptor import encrypting
            ret['footer'] = base64.b64decode(ret['footer'])

        del txt_json
        del data
        gc.collect()
        return ret
