import datetime


def rotate_bit_left(data_encrypt: bytes, chunk_size: int, rota: int):
    """Rotates one bit in a byte to the left by the specified position.

  Args:
      byte: The byte to rotate.
      position: The position of the bit to rotate (0-7).

  Returns:
      The rotated byte.
  """
    offset=0
    len_of_bytes = len(data_encrypt)
    data = data_encrypt[offset:offset + chunk_size]
    while len(data)>0:

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
            fr = ((data[i] << 1)&0b11111111) | first_bit
            ret += bytes([fr])
        except:
            print(bin(data[i]))
            print(bin((data[i] << 1)&0b11111111))
            print(bin((data[i] << 1) | first_bit))
            raise


        del data
        byte = bytes(ret)
        n = (datetime.datetime.utcnow() - t).total_seconds() * 1000
        print(f"{size} /{n}")
        offset+=chunk_size
        yield byte
        data = data_encrypt[offset:offset + chunk_size]


def rotate_bit_right(byte, position):
    """Rotates one bit in a byte to the right by the specified position.

  Args:
      byte: The byte to rotate.
      position: The position of the bit to rotate (0-7).

  Returns:
      The rotated byte.
  """
    mask = 1 << (7 - position)
    bit = (byte & mask) << (7 - position)
    return (byte >> 1) | bit
