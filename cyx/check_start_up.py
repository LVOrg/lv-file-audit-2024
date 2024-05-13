from cyx.common import config
from memcache import Client
from kazoo.client import KazooClient
import requests
import time
def check_url(url,method="get"):
    response = getattr(requests,method)(url)
    while response.status_code!=200:
        print(f"{url} is unavailable")
        print("re-connect on next 5 seconds")
        time.sleep(5)
        response = getattr(requests,method)(url)
    print(f"{url} is available")

def check_memcache():
    ok = False
    while not  ok:
        try:
            cache_server = config.cache_server
            print(f"Connect to {cache_server}")
            client = Client(tuple(cache_server.split(":")))
            ok = client.set("test","ok")
        except Exception as e:
            print(f"Error connecting to Memcached: {e}")
    print(f"Memcache server is ok run on {config.cache_server}")
def check_zookeeper():
    distribute_lock_server = config.distribute_lock_server
    ok = False
    while not ok:
        try:
            # Connect to Zookeeper
            zk = KazooClient(distribute_lock_server)
            zk.start()
            ok = True

        except Exception as e:
            print(f"Error connecting to Zookeeper: {e}")

        finally:
            # Close the Kazoo client connection
            zk.stop()
    print(f"zookeeper is ok {distribute_lock_server}")
check_url("https://api.trogiupluat.vn/swagger/index.html")
check_memcache()
check_zookeeper()