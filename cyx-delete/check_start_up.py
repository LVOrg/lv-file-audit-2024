print("Checking....")
from cyx.common import config
from memcache import Client
from kazoo.client import KazooClient
import requests
import time


def check_url(url, method="get"):
    ok= False
    while not ok:
        try:

            response = getattr(requests, method)(url)
            response.raise_for_status()
            ok= True
            print(f"{url} is available")
        except:
            print(f"{url} is unavailable re-connect on next 5 seconds")
            time.sleep(5)



def check_memcache():
    ok = False
    while not ok:
        try:
            cache_server = config.cache_server
            print(f"Connect to {cache_server}")
            client = Client(tuple(cache_server.split(":")))
            ok = client.set("test", "ok")
        except Exception as e:
            print(f"Error connecting to Memcached: {e}")
    print(f"Memcache server is ok run on {config.cache_server}")


def check_zookeeper():
    if not hasattr(config,"distribute_lock_server") or not isinstance(config.distribute_lock_server,str):
        raise Exception(f"distribute_lock_server was not found in config")
    distribute_lock_server = config.distribute_lock_server
    ok = False
    while not ok:
        try:
            # Connect to Zookeeper
            print(f"checking zookeeper {distribute_lock_server} ...")
            zk = KazooClient(distribute_lock_server)
            zk.start()
            ok = True
            print(f"checked zookeeper {distribute_lock_server} is ok")

        except Exception as e:
            print(f"Error connecting to Zookeeper: {e}")

        finally:
            # Close the Kazoo client connection
            zk.stop()
    print(f"zookeeper is ok {distribute_lock_server}")


check_url("https://api.trogiupluat.vn/swagger/index.html")
check_url(f"{config.remote_office}/hz")
check_url(f"{config.remote_pdf}/hz")
check_url(f"{config.remote_video}/hz")
check_memcache()

