import datetime
import time
import typing

from cyx.common import config
from memcache import Client
import cy_kit
from cyx.loggers import LoggerService
from typing import TypeVar

T = TypeVar('T')


class MemcacheServices:
    def __init__(self, logger=cy_kit.singleton(LoggerService)):
        self.server = config.cache_server
        self.client = Client(self.server.split(','))
        self.logger = logger

    def set_dict(self, key: str, data: dict, expiration=60 * 60 * 4) -> bool:
        assert isinstance(data, dict), "data must be dict"
        ret = self.client.set(key, data, time=expiration)
        return ret

    def set_object(self, key: str, data, expiration=60 * 60 * 4) -> bool:
        import cy_docs
        if isinstance(data,cy_docs.DocumentObject):
            ret = self.client.set(key, list(data.items()), time=expiration)
            return ret

        ret = self.client.set(key, data, time=expiration)
        return ret

    def get_object(self, key: str, cls: T) -> T:
        import cy_docs
        if cls==cy_docs.DocumentObject:
            ret_data = self.client.get(key)
            if ret_data is None:
                return  None
            if isinstance(ret_data,dict) and len(ret_data.keys())==0:
                return None
            ret= cy_docs.DocumentObject(**dict(ret_data))
            return ret


        ret = self.client.get(key)
        return ret

    def get_dict(self, key: str) -> dict:
        print(f"Get form cache dict key = {key}")
        return self.client.get(key)

    def get_str(self, key) -> str:
        return self.client.get(key)

    def set_str(self, key, value: str, expiration=60 * 60 * 4):
        return self.client.set(key, value, time=expiration)

    def delete_key(self, key: str):
        return self.client.delete(key)

    def set_bool_value(self, key, bool_value: bool, expiration=60 * 60 * 4):
        assert isinstance(bool_value, bool), "bool_value must be bool"
        ret = self.client.set(key, bool_value, time=expiration)
        return ret

    def get_bool_value(self, key) -> typing.Optional[bool]:
        ret = self.client.get(key)
        if ret is not None:
            assert isinstance(ret, bool), "Cache error"
        return ret

    def check_connection(self, timeout) -> bool:
        start_time = datetime.datetime.utcnow()
        self.logger.info(f"checking memcache server at {datetime.datetime.utcnow()} ...")
        print("check memcache server")

        def run_check():
            try:
                ret = self.client.set("check_connection", datetime.datetime.utcnow())
                if ret:
                    print(f"check memcache server {self.server} is ok")
                    self.logger.info(f"check memcache server {self.server} is ok at {datetime.datetime.utcnow()}")
                return ret

            except Exception as e:
                time.sleep(0.5)
                if (datetime.datetime.utcnow() - start_time).total_seconds() > timeout:
                    raise e
                else:
                    return run_check()

        return run_check()
