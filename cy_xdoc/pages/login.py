import cy_web
import fastapi
from cy_xdoc.pages.meta_data import get_meta_data
@cy_web.hanlder(method="get",path="login")
def login(request:fastapi.Request):
    return cy_web.render_template("index.html", {"request": request, "app": get_meta_data()})