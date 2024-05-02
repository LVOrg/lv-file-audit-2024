import time
import typing

import redis_lock

from cyx.common import config
from retry import retry
import hashlib

import time


cache_local= {}

from redis import Redis,StrictRedis
class DistributeLockService:
    def __init__(self):
        self.distribute_lock_server = config.distribute_lock_server
        self.conn : StrictRedis  = None
        self.do_start()
        self.lock= None
    @retry(delay=0.5,tries=100)
    def do_start(self):
        host,port = tuple(self.distribute_lock_server.split(":"))
        self.conn = StrictRedis(host=host,port=int(port))


    def accquire(self,lock_path)->redis_lock.Lock:
        return  redis_lock.Lock(self.conn,lock_path)


    def acquire_lock(self,lock_path):
        if cache_local.get(lock_path) is None:
            cache_local[lock_path] = redis_lock.Lock(self.conn, lock_path)
        return  cache_local[lock_path].acquire(blocking=False,timeout=10)
        # if self.lock is None:
        #     self.lock = redis_lock.Lock(self.conn, lock_path)
        # return self.lock.acquire(blocking=False,timeout=10)



    def release_lock(self,lock_path):
        if isinstance(cache_local.get(lock_path),redis_lock.Lock):
            cache_local.get(lock_path).release()
            del  cache_local[lock_path]