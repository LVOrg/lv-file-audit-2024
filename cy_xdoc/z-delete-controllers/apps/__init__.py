import cy_kit
from cy_xdoc.services.apps import AppServices
from fastapi import FastAPI, HTTPException
app_service = cy_kit.single(AppServices)
from fastapi import FastAPI, HTTPException
__cache_apps__ = dict()
def clear_cache():
    global __cache_apps__
    __cache_apps__.clear()
def check_app(get_app_name:str):
    global __cache_apps__
    if __cache_apps__.get(get_app_name):
        return
    ret = app_service.get_item('admin', app_get=get_app_name)
    if ret:
        __cache_apps__[get_app_name]=1
    else:
        raise HTTPException(status_code=404, detail="Item not found")

