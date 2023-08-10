import cy_web
from cyx.common import config
def get_meta_data():

    api_url= cy_web.get_host_url()+"/api"
    if config.get("api_url"):
        api_url = config.api_url
    return dict(
        version="1",
        full_url_app=cy_web.get_host_url(),
        full_url_root=cy_web.get_host_url(),
        api_url=api_url,
        host_dir=cy_web.get_host_dir()
    )