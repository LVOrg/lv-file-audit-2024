import datetime


def print_bytes(fx):
    if not isinstance(fx, bytes):
        fx = bytes([fx])
    ret = []
    for x in fx:
        r = bin(x).split('b')[1]
        r = (8 - len(r)) * "0" + r
        ret += [r]
    print(" ".join(ret))


def encrypt_content(data_encrypt: bytes, chunk_size: int, rota: int, first_data):
    """Rotates one bit in a byte to the left by the specified position.

  Args:
      byte: The byte to rotate.
      position: The position of the bit to rotate (0-7).

  Returns:
      The rotated byte.
  """
    offset = 0
    len_of_bytes = len(data_encrypt)
    if len_of_bytes == 0:
        return bytes([])
    data = data_encrypt[offset:offset + chunk_size]
    while len(data) > 0:

        mask = 0b10000000

        first_bit = (first_data >> 7)

        ret = []
        size = len(data)
        i = 0
        while i < size - 1:
            a = (data[i] << 1) & 0b011111111
            b = data[i + 1]
            bb = (b & mask) >> 7
            a = a | bb
            ret += bytes([a])
            i += 1
        try:
            fr = ((data[i] << 1) & 0b11111111) | first_bit
            ret += bytes([fr])
        except Exception as ex:
            raise ex

        del data
        byte = bytes(ret)
        offset += chunk_size
        yield byte
        data = data_encrypt[offset:offset + chunk_size]


def decrypt_content(data_encrypt: bytes, chunk_size: int, rota: int,first_data):
    pos = 0
    buffer = data_encrypt[pos:pos + chunk_size]
    buffer_len = len(buffer)
    while buffer_len > 0:
        i = 0
        last_bit = (first_data & 0b00000001) << 7

        ret = []

        while i < buffer_len - 1:
            rb = (buffer[i] >> 1) | last_bit
            # print_bytes(rb)
            last_bit = (buffer[i] & 0b00000001) << 7
            ret += [rb]
            i += 1
        rb = (buffer[buffer_len - 1] >> 1) | (buffer[buffer_len - 2] & 0b00000001)
        ret += [rb]
        yield bytes(ret)
        pos += chunk_size
        buffer = data_encrypt[pos:pos + chunk_size]
        buffer_len = len(buffer)
