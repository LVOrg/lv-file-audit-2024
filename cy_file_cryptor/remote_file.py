from cy_file_cryptor.remote_file_io import IORemote
def do_open(
        url_file,
        original_open_file,
        send_kwargs):
    return IORemote(
        url_file = url_file,
        original_open_file=original_open_file,
        send_kwargs = send_kwargs
    )