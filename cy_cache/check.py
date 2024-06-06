from cy_cache.memcache_data import cy_caching, set_up
from cyx.repository import Repository
set_up("localhost:11211")
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
@cy_caching()
def get_by_id(app_name,upload_id) :
    ret= Repository.files.app(app_name).context.find_one(
        Repository.files.fields.id==upload_id
    ).to_json_convertable()

    fx= CacheDoc()
    for k,v in ret.items():
        setattr(fx,k,v)
    return fx



fx = Test()
x= get_by_id(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")
x._id="123"
print(x)

x2= get_by_id(app_name="lv-docs",upload_id="908c602f-4183-46d9-8f45-3b81619a7ca2")