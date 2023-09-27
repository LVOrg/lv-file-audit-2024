from cyx.common import config
from memcache import Client, _Host, SERVER_MAX_KEY_LENGTH, SERVER_MAX_VALUE_LENGTH


class MemcacheServices:
    def __init__(self):
        self.server = [config.cache_server]
        self.client = Client(self.server)

    def set_dict(self, key: str, data: dict, expiration=60 * 60 * 4) -> bool:
        assert isinstance(data, dict), "data must be dict"
        ret = self.client.set(key, data, time=expiration)
        return ret

    def get_dict(self, key: str) -> dict:
        return self.client.get(key)

    def delete_key(self, key: str):
        return self.client.delete(key)
