import io

import requests


class IORemote(object):
    def __init__(self, url_file: str,filename:str, original_open_file, send_kwargs):
        self.url_file = url_file
        self.original_open_file = original_open_file
        self.send_kwargs = send_kwargs
        self.pos = 0
        self.header = {'Range': f'bytes={self.pos}-'}
        self.raw_header = self.send_kwargs.get('header')
        if isinstance(self.send_kwargs.get('header'), dict):
            self.header = {**self.header, **self.send_kwargs.get('header')}
        self.response = None
        self.file_size = None
        self.filename = filename

    def __enter__(self):
        self.header["Range"] = 'bytes=0-0'
        self.response = requests.get(self.url_file, headers=self.header,stream=True)
        self.response.raise_for_status()  # Raise an exception for non-200 status codes

        if 'content-range' in self.response.headers:
            self.file_size = int(self.response.headers['content-range'].split('/')[1])

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self, *args, **kwargs):  # real signature unknown
        if self.response:
            self.response.close()

    def fileno(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def flush(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def isatty(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def readable(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def readline(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def readlines(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def seek(self, *args, **kwargs):
        if len(args) == 1:
            self.pos = args[0]
        elif len(args) == 2:
            if args[1] == io.SEEK_SET:
                self.pos = args[0]
            elif args[1] == io.SEEK_CUR:
                self.pos += args[0]
            elif args[1] == io.SEEK_END:
                self.pos = self.file_size + args[0]
            else:
                raise ValueError("the second arg mut be in [0,1,2]")

    def seekable(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def tell(self, *args, **kwargs):  # real signature unknown
        return self.pos

    def truncate(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def writable(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def writelines(self, *args, **kwargs):  # real signature unknown
        raise NotImplemented()

    def read(self, *args, **kwargs):
        if len(args) == 0:
            self.header["Range"] = 'bytes=0-'
            self.response = requests.get(self.url_file, headers=self.header)
            self.response.raise_for_status()  # Raise an exception for non-200 status codes
            ret_data = self.response.content
            self.pos= self.file_size
            return ret_data
        else:
            self.header["Range"] = f'bytes={self.pos}-{self.pos+args[0]}'
            self.response = requests.get(self.url_file, headers=self.header)
            self.response.raise_for_status()  # Raise an exception for non-200 status codes
            ret_data = self.response.content
            self.pos+=args[0]
            return ret_data


        raise NotImplemented()
