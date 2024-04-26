import time

import redis

from cyx.common import config

import time

class DistributeLockService:
    def __init__(self):
        redis_host = config.redis_server.split(':')[0]  # Replace with your Redis host
        redis_port = int(config.redis_server.split(':')[1] )  # Replace with your Redis port
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)


    def start(self):
        pass
    def acquire_lock(self, lock_path, timeout=60):
        """Acquires a distributed lock using Zookeeper.

        Args:
            lock_path: The path in ZooKeeper to use for the lock.
            timeout: The maximum time to wait for the lock in seconds (optional).

        Returns:
            True if the lock is acquired, False otherwise.
        """
        lock_key = f"lock:{lock_path}"  # Prefix lock name for clarity
        acquired = self.redis_client.setnx(lock_key, 1)
        if acquired:
            # Set an expiration time for the lock to prevent indefinite holding
            self.redis_client.expire(lock_key, timeout + 1)  # Set expiration slightly longer than timeout
        return acquired

    def release_lock(self, lock_path):
        lock_key = f"lock:{lock_path}"
        script = """
          if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
          else
            return 0
          end
          """
        """Releases the acquired distributed lock.

           Args:
               lock_name: The name of the lock to release.
           """

        script = """
           if redis.call('get', KEYS[1]) == ARGV[1] then
               return redis.call('del', KEYS[1])
           else
               return 0
           end
           """
        self.redis_client.eval(script, keys=[lock_key], args=[self.redis_client.get(lock_key).decode('utf-8')])

