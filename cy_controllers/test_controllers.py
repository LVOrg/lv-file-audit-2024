from pydantic import BaseModel
from fastapi_router_controller import Controller
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter()
controller = Controller(router)
security = HTTPBasic()
def verify_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == "john"
    correct_password = credentials.password == "silver"
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect auth",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

class Foo(BaseModel):
    bar: str = "wow"


async def amazing_fn():
    return Foo(bar="amazing_variable")


@controller.resource()
class ExampleController:

    # add class wide dependencies e.g. auth
    dependencies = [Depends(verify_auth)]

    # you can define in the Controller init some FastApi Dependency and them are automatically loaded in controller methods
    def __init__(self, x: Foo = Depends(amazing_fn)):
        self.x = x

    @controller.route.get(
        "/some_api", summary="A sample description", response_model=Foo
    )
    def sample_api(self):
        print(self.x.bar)  # -> amazing_variable
        return self.x
