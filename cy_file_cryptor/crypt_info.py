import base64
import datetime
import gc
import json
import os.path
import threading
import uuid
import numpy as np
from cryptography.fernet import Fernet
__buffer_cache__ = {}

def write_dict(data: dict, file_path, original_open):
    global __buffer_cache__
    __buffer_cache__[file_path] =data
    def __save_file__():
        with original_open(file_path, "wb") as fs:
            txt_json = json.dumps(data)
            data_json = np.frombuffer(txt_json.encode(), dtype=np.uint8)
            data_json = ~data_json
            fs.write(data_json.tobytes())
    threading.Thread(target=__save_file__,args=()).start()


def write_dict_beta(data: dict, file_path, original_open):
    # key = uuid.UUID("14b9fdee-cb1c-4180-b9c3-78e26b44e77b").bytes + \
    #       uuid.UUID("869edadd-35df-4615-9de3-95e98835d3ab").bytes
    key = b'\x14\xb9\xfd\xee\xcb\x1cA\x80\xb9\xc3x\xe2kD\xe7{\x86\x9e\xda\xdd5\xdfF\x15\x9d\xe3\x95\xe9\x885\xd3\xab'
    bas64_key = b'FLn97sscQYC5w3jia0Tne4ae2t0130YVneOV6Yg106s='

    fernet = Fernet(bas64_key)
    tem_header = None
    tem_footer = None
    data['header'] = data.get('header', bytes([]))
    data['footer'] = data.get('footer', bytes([]))
    if isinstance(data['header'], bytes):
        tem_header = data['header']
        data['header'] = base64.b64encode(tem_header).decode("utf-8")
        data['header_size'] = len(tem_header)
    if isinstance(data['footer'], bytes):
        tem_footer = data['footer']
        data['footer'] = base64.b64encode(tem_footer).decode("utf-8")
        data['footer_size'] = len(tem_footer)
    txt_json = json.dumps(data)
    encrypted_text = fernet.encrypt(txt_json.encode('utf8'))
    with original_open(file_path, "wb") as f:
        f.write(encrypted_text)
    if tem_header:
        data['header'] = tem_footer
    if tem_footer:
        data['footer'] = tem_footer


def read_dict(file_path, original_open) -> dict:
    if isinstance(__buffer_cache__.get(file_path),dict):
        return __buffer_cache__[file_path]
    else:
        with original_open(file_path, "rb") as f:
            data = f.read()
            data_json = np.frombuffer(data, dtype=np.uint8)
            data_json = ~data_json
            ret = json.loads(data_json.tobytes().decode())
            __buffer_cache__[file_path] = ret
        return __buffer_cache__[file_path]



def read_dict_beta(file_path, original_open) -> dict:
    t = datetime.datetime.utcnow()
    # key = uuid.UUID("14b9fdee-cb1c-4180-b9c3-78e26b44e77b").bytes + \
    #       uuid.UUID("869edadd-35df-4615-9de3-95e98835d3ab").bytes
    key = b'\x14\xb9\xfd\xee\xcb\x1cA\x80\xb9\xc3x\xe2kD\xe7{\x86\x9e\xda\xdd5\xdfF\x15\x9d\xe3\x95\xe9\x885\xd3\xab'
    bas64_key = b'FLn97sscQYC5w3jia0Tne4ae2t0130YVneOV6Yg106s='

    fernet = Fernet(bas64_key)
    with original_open(file_path, "rb") as f:
        data = f.read()
        txt_json = fernet.decrypt(data).decode('utf8')
        ret = json.loads(txt_json)
        if ret.get('header'):
            from cy_file_cryptor import encrypting
            ret['header'] = base64.b64decode(ret['header']) or bytes([])
        if ret.get('footer'):
            from cy_file_cryptor import encrypting
            ret['footer'] = base64.b64decode(ret['footer']) or bytes([])
        if ret.get('header_size') and isinstance(ret['header'], bytes):
            ret['header'] = ret['header'][0:ret['header_size']]
        if ret.get('footer_size') and isinstance(ret['footer'], bytes):
            ret['footer'] = ret['footer'][0:ret['footer_size']]

        del txt_json
        del data
        gc.collect()
        n = (datetime.datetime.utcnow() - t).total_seconds() * 1000
        print(f"read {file_path} spent {n} ms")
        return ret
