from cy_cache.memcache_data import cy_caching, set_up
from cyx.repository import Repository
set_up("localhost:11211")
from cy_cache.test_1 import get_by_id as get_2
#@caching()
import cy_kit
# class Test001:
#     @cy_caching()
#     @classmethod
#     def cong(cls, param, param1):
#         pass
# tx = cy_kit.singleton(Test001)
# v=tx.cong(1,1)
import uuid


class SubClass:
    id: str


@cy_caching(keys=["code"])
class Test:
    code: str
    name: str

    def __init__(self, my_code: str = "A"):
        self.code = uuid.uuid4()

class CacheDoc:
    def __setattr__(self, key, value):
        print(key)
import cy_kit
class MyCode:
    @cy_caching()
    def get_by_id(self, app_name,upload_id) :
        ret= Repository.files.app(app_name).context.find_one(
            Repository.files.fields.id==upload_id
        ).to_json_convertable()

        fx= CacheDoc()
        for k,v in ret.items():
            setattr(fx,k,v)
        return fx
ins= cy_kit.singleton(MyCode)
get_2.__clear_cache__()
# get_by_id.__clear_cache__()

fx = Test()
x= ins.get_by_id(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")
x2= ins.get_by_id(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")
ins.get_by_id.__clear_cache__(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")
x= ins.get_by_id(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")
x._id="123"
print(x)

x2= ins.get_by_id(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")