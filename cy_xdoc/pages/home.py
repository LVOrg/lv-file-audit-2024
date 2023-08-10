import fastapi
from fastapi import Depends, Response
import cy_web
from cy_xdoc.pages.meta_data import get_meta_data
import os


@cy_web.hanlder(method="get",path="")
def home_page(request:fastapi.Request):
    app_data = dict(
        version="1",
        full_url_app=cy_web.get_host_url(),
        full_url_root=cy_web.get_host_url(),
        api_url=cy_web.get_host_url()+"/api",
        host_dir=cy_web.get_host_dir()
    )
    return cy_web.render_template(
        rel_path_to_template="index.html",
        render_data={"request": request,"app": get_meta_data()}
    )
