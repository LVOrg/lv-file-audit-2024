import cy_web
from cyx.common import config
from fastapi.requests import Request
def get_meta_data(request):
    use_ssl = False
    if hasattr(config, "use_ssl") and config.use_ssl == "on":
        use_ssl = True
    api_url=cy_web.get_host_url(request,use_ssl)+"/api"
    if config.get("api_url"):
        api_url = config.api_url
    return dict(
        version="1",
        full_url_app=cy_web.get_host_url(request,use_ssl),
        full_url_root=cy_web.get_host_url(request,use_ssl),
        api_url=api_url,
        host_dir=cy_web.get_host_dir()
    )