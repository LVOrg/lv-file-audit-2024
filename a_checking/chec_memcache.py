from a_checking.test_class import EMP
fx= EMP()
fx.code="123"
import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
cache = cy_kit.singleton(MemcacheServices)
cache.set_object("long-test",fx)