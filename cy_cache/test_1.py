from cy_cache.memcache_data import cy_caching
from cyx.repository import Repository
@cy_caching()
def get_by_id(app_name,upload_id) :
    ret= Repository.files.app(app_name).context.find_one(
        Repository.files.fields.id==upload_id
    ).to_json_convertable()

    fx= object()
    for k,v in ret.items():
        setattr(fx,k,v)
    return fx