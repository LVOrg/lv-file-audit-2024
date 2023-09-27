import datetime
import time
import typing

from cyx.common import config
from memcache import Client, _Host, SERVER_MAX_KEY_LENGTH, SERVER_MAX_VALUE_LENGTH
import cy_kit
from cyx.loggers import LoggerService


class MemcacheServices:
    def __init__(self, logger=cy_kit.singleton(LoggerService)):
        self.server = config.cache_server
        self.client = Client(self.server.split(','))
        self.logger = logger

    def set_dict(self, key: str, data: dict, expiration=60 * 60 * 4) -> bool:
        assert isinstance(data, dict), "data must be dict"
        ret = self.client.set(key, data, time=expiration)
        return ret

    def get_dict(self, key: str) -> dict:
        print(f"Get form cache dict key = {key}")
        return self.client.get(key)

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


    def check_connection(self, timeout)->bool:
        start_time = datetime.datetime.utcnow()
        self.logger.info(f"checking memcache server at {datetime.datetime.utcnow()} ...")
        print("check memcache server")
        def run_check():
            try:
                ret = self.client.set("check_connection",datetime.datetime.utcnow())
                if ret:
                    print(f"check memcache server {self.server} is ok")
                    self.logger.info(f"check memcache server {self.server} is ok at {datetime.datetime.utcnow()}")
                return ret

            except Exception as e:
                time.sleep(0.5)
                if (datetime.datetime.utcnow()-start_time).total_seconds()>timeout:
                    raise e
                else:
                    return run_check()

        return run_check()

