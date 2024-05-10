import threading
import time
import typing

import redis_lock

from cyx.common import config
from retry import retry
import hashlib

import time

cache_local = {}

from redis import Redis, StrictRedis
from kazoo.client import KazooClient,KazooState
from kazoo.recipe.lock import Lock
__zk__: KazooClient = None
__lock__ = dict()
__local__lock__: threading.Lock = threading.Lock()

class DistributeLockService:
    def __init__(self):

        self.distribute_lock_server = config.distribute_lock_server

        self.do_start()
        self.lock = None

    # @retry(delay=0.5, tries=100)
    def do_start(self):
        global __zk__
        if __zk__ is None:
            __zk__ = KazooClient(self.distribute_lock_server)
            __zk__.start()

    # def accquire(self,lock_path)->redis_lock.Lock:
    #     return  redis_lock.Lock(self.conn,lock_path)

    def acquire_lock(self, lock_path):
        global __lock__
        global __local__lock__
        ret = None
        if not __lock__.get(lock_path) or not hasattr(__lock__.get(lock_path),"acquire"):
            __lock__[lock_path] = __zk__.Lock(lock_path)
        return __lock__[lock_path].acquire(timeout=30)

        # if cache_local.get(lock_path) is None:
        #     cache_local[lock_path] = redis_lock.Lock(self.conn, lock_path)
        # return  cache_local[lock_path].acquire(blocking=False,timeout=10)
        # # if self.lock is None:
        # #     self.lock = redis_lock.Lock(self.conn, lock_path)
        # # return self.lock.acquire(blocking=False,timeout=10)

    def release_lock(self, lock_path):
        global __lock__
        if __lock__.get(lock_path) and hasattr(__lock__.get(lock_path),"release"):
            __lock__.get(lock_path).release()
            __lock__[lock_path]=False
