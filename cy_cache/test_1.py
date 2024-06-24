from cy_cache.memcache_data import cy_caching
from cyx.repository import Repository
from cy_cache.function_cache import caching,set_up
from cy_docs import DocumentObject
from cy_xdoc.models.files import DocUploadRegister
set_up("localhost:11211")
class FX:
    @caching()
    def test(self):
        print("Ok")
fx= FX()
@caching()
def get_by_id(app_name:str,upload_id:str)->DocumentObject[DocUploadRegister]|None:
    ret= Repository.files.app(app_name).context.find_one(
        Repository.files.fields.id==upload_id
    )

    return ret
ret_data=get_by_id(app_name="lv-docs",upload_id= "e0c1ea07-1a7d-4163-9205-6b819db7cbc3")
print(ret_data.id)