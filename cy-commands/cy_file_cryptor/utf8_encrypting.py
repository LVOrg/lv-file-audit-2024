import datetime


def encrypt_content(data_encrypt: bytes, chunk_size: int, rota: int):
    """Rotates one bit in a byte to the left by the specified position.

  Args:
      byte: The byte to rotate.
      position: The position of the bit to rotate (0-7).

  Returns:
      The rotated byte.
  """
    offset = 0
    len_of_bytes = len(data_encrypt)
    data = data_encrypt[offset:offset + chunk_size]
    while len(data) > 0:

        t = datetime.datetime.utcnow()
        mask = 0b10000000

        first_bit = (data[0] >> 7)

        ret = []
        size = len(data)
        i = 0
        while i < size - 1:
            a = (data[i] << 1) & 0b11111111
            b = data[i + 1]
            bb = (b & mask) >> 7
            a = a | bb
            ret += bytes([a])
            i += 1
        try:
            fr = ((data[i] << 1) & 0b11111111) | first_bit
            ret += bytes([fr])
        except:
            print(bin(data[i]))
            print(bin((data[i] << 1) & 0b11111111))
            print(bin((data[i] << 1) | first_bit))
            raise

        del data
        byte = bytes(ret)
        n = (datetime.datetime.utcnow() - t).total_seconds() * 1000
        print(f"{size} /{n}")
        offset += chunk_size
        yield byte
        data = data_encrypt[offset:offset + chunk_size]


def decrypt_content(data_encrypt: bytes, chunk_size: int, rota: int):
    pos=0
    buffer = data_encrypt[pos:pos+chunk_size]
    buffer_len = len(buffer)
    while buffer_len>0:
        i=0
        last_bit = (buffer[buffer_len - 1] & 0b00000001) << 7
        first_bit = buffer[0] & 0b10000000
        ret=[]
        t=datetime.datetime.utcnow()
        while i<buffer_len-1:
            rb = (buffer[i] >> 1) | last_bit
            last_bit = buffer[i] & 0b00000001
            ret+=[rb]
            i+=1
        rb = (buffer[buffer_len - 1] >> 1) | (ret[0] & 0b10000000)
        ret+=[rb]
        yield bytes(ret)
        n= (datetime.datetime.utcnow()-t).total_seconds()*1000
        print(n)
        pos+=chunk_size
        buffer = data_encrypt[pos:pos + chunk_size]
        buffer_len = len(buffer)
