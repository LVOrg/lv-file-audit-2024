# import os
# import pathlib
# from OpenSSL import crypto
# from jose.jwt import get_unverified_claims
# # get_unverified_claims()
# from cryptography.x509 import load_pem_x509_certificate
# # from cryptography.hazmat.primitives.serialization..jwt import JWTClaims, JWTBuilder, JWTHeader
# cert_path = os.path.join(pathlib.Path(__file__).parent.__str__(),"OfficeWopi.pfx")
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.serialization import (
#     pkcs12,
#     Encoding,
#     PublicFormat,
#     PrivateFormat,
#     KeySerializationEncryption,
#     BestAvailableEncryption,
#     NoEncryption,
#
#
# )
# fx= KeySerializationEncryption()
# import base64
# test_data = pkcs12.load_key_and_certificates(data=open(cert_path, 'rb').read(),password="dxwopi".encode('utf8'))
# private_key=test_data[0].private_bytes(Encoding.DER,PrivateFormat.PKCS8,NoEncryption())
# fx_private_key = serialization.load_der_private_key(
#     private_key, password=None, backend=default_backend()
# )
# prvate_key =serialization.load_pem_public_key(
#     data=open(cert_path, 'rb').read()
# )
# p12 = pkcs12.load_pkcs12(open(cert_path, 'rb').read(), "dxwopi".encode('utf8'))
# bytes_key =p12.key.public_key().public_bytes(Encoding.DER,PublicFormat.SubjectPublicKeyInfo)
# base64_key = base64.b64encode(bytes_key).decode('utf8')
# kf = BestAvailableEncryption(password="dxwopi".encode('utf8'))
#
# bytes_p_key = p12.key.private_bytes(Encoding.DER,PrivateFormat.PKCS8,kf)
# bytes_p_key = p12.key.private_bytes(Encoding.DER,PrivateFormat.PKCS8,kf)
# base64_p_key = base64.b64encode(bytes_p_key).decode('utf8')
# # get various properties of said file.
# # note these are PyOpenSSL objects, not strings although you
# # can convert them to PEM-encoded strings.
# p12.get_certificate()     # (signed) certificate object
# p12.get_privatekey()      # private key.
# p12.get_ca_certificates() # ca chain.