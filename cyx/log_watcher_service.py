import threading

import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
import functools


class LogWatcherServices:
    def __init__(self, memcache_services=cy_kit.singleton(MemcacheServices)):
        self.memcache_services = memcache_services

    @functools.cache
    def get_pod_name(self):
        f = open('/etc/hostname')
        pod_name = f.read()
        f.close()
        full_pod_name = pod_name.lstrip('\n').rstrip('\n')
        items = full_pod_name.split('-')
        if len(items) > 2:
            pod_name = "-".join(items[:-2])
        else:
            pod_name = full_pod_name
        return pod_name

    def logs(self, content):
        def running():
            log_cache = self.memcache_services.get_dict(f"{type(self).__module__}/{type(self).__name__}")
            if not isinstance(log_cache, dict):
                log_cache = dict()
                log_cache[self.get_pod_name()] = []
            if len(log_cache[self.get_pod_name()]) > 10:
                log_cache[self.get_pod_name()] = log_cache[self.get_pod_name()][1:]
            log_cache[self.get_pod_name()] += [content]
            self.memcache_services.set_dict(f"{type(self).__module__}/{type(self).__name__}",log_cache)
        threading.Thread(target=running).start()
