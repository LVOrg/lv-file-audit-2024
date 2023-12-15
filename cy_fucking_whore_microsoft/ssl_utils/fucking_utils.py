import os
import pathlib
import typing
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.serialization import (
    pkcs12,
    Encoding,
    PublicFormat,
    PrivateFormat,
    KeySerializationEncryption,
    BestAvailableEncryption,
    NoEncryption,

)
import jwt
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

ALGORITHM = "RS256"
cert_path = os.path.join(pathlib.Path(__file__).parent.__str__(), "OfficeWopi.pfx")


def get_fucking_private_key(pfx_password: str,
                            encryptor_password: typing.Optional[str] = None,
                            pfx_file_path: typing.Optional[str] = None):
    """
    The function read the fucking PFX file.
    pfx_password is the fucking password to read PFX file.
    encryptor_password is the factor to generate private key. That shit can be empty if it need not
    :param pfx_password: pfx_password is the fucking password to read PFX file
    :param encryptor_password: encryptor_password is the factor to generate private key. That shit can be empty if it need not
    :param pfx_file_path: absolute path to pfx file
    :return:
    """
    if pfx_file_path is None:
        pfx_file_path = cert_path
    private_key_handler, _, _ = pkcs12.load_key_and_certificates(data=open(pfx_file_path, 'rb').read(),
                                                                 password=pfx_password.encode('utf8'))
    encryptor = NoEncryption()
    if encryptor_password is not None:
        encryptor = BestAvailableEncryption(password=encryptor_password.encode('utf8'))
    private_key = private_key_handler.private_bytes(Encoding.DER, PrivateFormat.PKCS8, encryptor)
    ret = serialization.load_der_private_key(
        private_key, password=None, backend=default_backend()
    )
    return ret


class FuckingAccessTokenInfo:
    """
    This fucking struct including 2 properties
    The fucking first is  access_token. The shit is text can be use by https://token.dev for inspection.
    The second bullshit is access_token_ttl (Fucking TTL is stand for Time To Live).
    The unit of second fucking property is millisecond since 01/01/1970 to expire time of token
    """
    access_token: str
    """
    Fucking access token content in text
    """
    access_token_ttl: int
    """
    The fucking time to live of access token in millisecaccess_token_ttlond
    """
    def __init__(self, access_token: str, access_token_ttl:int):
        self.access_token = access_token
        self.access_token_ttl = access_token_ttl

def generate_fucking_token(
        issuer: str,
        audience: str,
        unique_name: str,
        container: str,
        docid: str,
        private_key) -> FuckingAccessTokenInfo:
    """
    The step is fucking to get private key from PFX file by calling get_fucking_private_key
    The fucking shit function return token for WOPI and expire time of token since 01/01/1970 in millisecond unit
    :param issuer:
    :param audience:
    :param unique_name:
    :param container:
    :param docid:
    :param private_key:
    :return:
    """
    expr = datetime.utcnow() + timedelta(days=1)
    claims = {
        "iss": issuer,
        "aud": audience,
        "nbf": datetime.utcnow(),
        "exp": expr,  # Set expiration time
        "unique_name": unique_name,
        "container": container,
        "docid": docid

    }

    access_token = jwt.encode(claims, private_key, algorithm=ALGORITHM)
    access_token_ttl = (expr-datetime(1970,1,1)).total_seconds()*1000
    return FuckingAccessTokenInfo(
        access_token_ttl=access_token_ttl,
        access_token = access_token
    )
