from fastapi import Depends, Response,Request
import cy_web
import os
from cy_xdoc.pages.meta_data import get_meta_data
@cy_web.hanlder(method="get",path= "{directory:path}")
async def page_single(directory: str ,request: Request):

    directory = directory.split('?')[0]
    check_dir_path = os.path.join(cy_web.get_static_dir(), "views", directory.replace('/', os.sep))

    if not os.path.exists(check_dir_path):
        return Response(status_code=401)

    return cy_web.render_template("index.html", {"request": request, "app": get_meta_data()})
