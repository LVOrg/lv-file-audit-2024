import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())
from cyx.cache_service.memcache_service import MemcacheServices
import cy_kit
mc = cy_kit.singleton(MemcacheServices)
mc.set_dict("long-test",dict(
    a=1,
    b=2
))
fx= mc.get_dict("long-test")
print(fx)