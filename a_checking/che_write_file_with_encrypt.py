from rsa.cli import encrypt

fx=r'/mnt/files/developer/2024/08/22/png/2c7cb474-2fba-423b-a6ae-9d989434404f/avatarthu aug 22 2024 13:26:30 gmt+0700 _indochina time_.png-version-1'
fx=fx.replace(":","_").replace("+","_")
import cy_file_cryptor.wrappers
import cy_file_cryptor.context
cy_file_cryptor.context.set_server_cache("localhost:11211")
with open(fx,mode="wb",encrypt=True,chunk_size_in_kb=0,file_size=512) as fs:
    fs.write("dsadadadadadadadadasdasdadadad".encode())