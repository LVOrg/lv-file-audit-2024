__cache_server__ = None

import functools
import os

from memcache import Client
import hashlib
import functools
if hasattr(functools,"cache"):
    from functools import cache as fr_cache

else:
    def ft_cache(*args,**kwargs):
        return functools.lru_cache(maxsize = 128)(*args,**kwargs)
import typing
__client__:  typing.Union[Client,None] = None
__url__ = None

__cache_data__ = {}
__revert_cache_data__ = {}

__permanent_cache__ = {}
def hash_key_sha256(text):
    """Hashes the provided text using SHA-256 and returns the hexadecimal string.

  Args:
      text: The text content to be hashed.

  Returns:
      The SHA-256 hash of the text in hexadecimal format.
  """
    global __cache_data__
    global __revert_cache_data__
    if isinstance(__cache_data__.get(text), str):
        return __cache_data__[text]
    # Encode the text as bytes (UTF-8 is common)
    text_bytes = text.encode("utf-8")

    # Create a SHA-256 hash object
    hasher = hashlib.sha256()

    # Update the hasher with the text bytes
    hasher.update(text_bytes)

    # Convert the hash digest to hexadecimal string
    ret_value = hasher.hexdigest()
    __cache_data__[text] = ret_value
    return ret_value


def set_server_cache(url: str):
    global __url__
    __url__ = url.split(',')


def write_to_cache(key: str, data: dict):
    global __permanent_cache__
    global __client__
    global __url__
    if __client__ is None:
        __client__ = Client(__url__)
    memcache_key = hash_key_sha256(key)
    __permanent_cache__[memcache_key] = data
    ret = __client__.set(memcache_key, data, time=24 * 60 * 60)

        # raise Exception(f"Can not cache data to {__url__}")


@ft_cache
def get_key(key: str):
    return hash_key_sha256(key)


def read_from_cache(key: str):
    global __permanent_cache__
    global __client__
    global __url__
    if __client__ is None:
        __client__ = Client(__url__)
    memcache_key = get_key(key)
    ret = __client__.get(memcache_key)
    return ret


def clear_cache(key: str):
    global __client__
    global __url__
    if __client__ is None:
        __client__ = Client(__url__)
    memcache_key = get_key(key)
    ret = __client__.delete(memcache_key)
    return ret


class EncryptContext:
    def __init__(self, file_will_be_encrypt: str):
        self.file_path = file_will_be_encrypt
        self.encryptor_file = f"{file_will_be_encrypt}.cryptor"
        from cy_file_cryptor.crypt_info import write_dict
        from cy_file_cryptor.wrappers import original_open_file
        from cy_file_cryptor.writer_binary_v02 import __max_wrap_size__, __min_wrap_size__

        write_dict(dict(is_crypted=True, chunk_size=1024 * 64), self.encryptor_file, original_open_file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __enter__(self):
        return self


def create_encrypt(file_path: str) -> EncryptContext:
    return EncryptContext(file_path)
