from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Request, Response,status
app = FastAPI()

security = HTTPBasic()
import cy_web
import cy_kit
import cyx.common.basic_auth
auth_service = cy_kit.singleton(cyx.common.basic_auth.BasicAuth)
@cy_web.hanlder(method="get", path="users/me")
@app.get("/users/me")
def read_current_user(request:Request):
    res= Response(status_code=status.HTTP_401_UNAUTHORIZED,

                            headers={"WWW-Authenticate": 'Basic realm="simple"'})
    return res