from cy_encryptors.text_encryptor import encode,decode
bff = encode("Hello".encode())
fx= decode(bff)
print(bff.decode("utf8"))