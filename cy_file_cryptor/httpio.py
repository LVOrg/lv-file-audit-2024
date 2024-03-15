import requests
import io


class IORemote(io.BytesIO):
    def __init__(self,
                 url: str,
                 web_method="get",
                 request_header={},
                 request_body=None
                 ):
        self.url_file = url
        self.pos = 0
        self.header = {'Range': f'bytes={self.pos}-'}
        self.web_method = web_method
        self.request_header = request_header
        self.request_body = request_body
        self.header = {**self.header, **self.request_header}
        self.response = None
        self.file_size = None

    def __enter__(self):
        self.header["Range"] = 'bytes=0-0'
        self.response = getattr(requests, self.web_method)(self.url_file, headers=self.header)
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
            self.pos = self.file_size
            return ret_data
        else:
            self.header["Range"] = f'bytes={self.pos}-{self.pos + args[0]}'
            self.response = requests.get(self.url_file, headers=self.header)
            self.response.raise_for_status()  # Raise an exception for non-200 status codes
            ret_data = self.response.content
            self.pos += args[0]
            return ret_data

        raise NotImplemented()
