import pathlib
import typing
from typing import List
import sys

import fastapi

import cy_web

sys.path.append(pathlib.Path(__file__).parent.__str__())
# sys.path.append(r"/home/vmadmin/python/v6/file-service-02/build/lib.linux-x86_64-3.8/cy_web")
# from cy_web import cy_web_x
import cy_web_x


def create_web_app(
        working_dir: str,

        static_dir: str,
        template_dir: str,
        logs_dir: str = "./logs",
        bind: str = "0.0.0.0:80",
        url_get_token: str = "api/accounts/token",
        jwt_algorithm: str = "HS256",
        jwt_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        dev_mode: bool = False,
        cache_folder:str="./cache",
        host_url: str=None,
):
    import socket
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    if host_url is None:
        host_url = f"http://{IPAddr}:{bind.split(':')[1]}"
    ret = cy_web_x.WebApp(

        working_dir=working_dir,
        host_url=host_url,
        static_dir=static_dir,
        template_dir=template_dir,
        logs_dir=logs_dir,
        dev_mode=dev_mode,
        url_get_token=url_get_token,
        jwt_algorithm=jwt_algorithm,
        jwt_secret_key=jwt_secret_key,
        bind=bind,
        cache_folder=cache_folder

    )
    return ret


def hanlder(method: str, path: str):
    return cy_web_x.web_handler(
        method=method,
        path=path
    )


def load_controller_from_dir(prefix, path):
    return cy_web_x.load_controller_from_dir(
        prefix,
        path
    )


def start_with_uvicorn(worker=4):
    print(cy_web.get_host_url())
    cy_web_x.start_with_uvicorn(worker)
def start_with_guicorn(worker=4):
    print(cy_web.get_host_url())
    cy_web_x.start_with_guicorn(worker)

def middleware():
    return cy_web_x.middleware()








def add_cors(origins: List[str]):
    return cy_web_x.add_cors(origins)


def get_host_url():
    return cy_web_x.get_host_url()


def get_host_dir():
    return cy_web_x.get_host_dir()


def render_template(rel_path_to_template, render_data):
    return cy_web_x.render_template(rel_path_to_template, render_data)


def get_static_dir() -> str:
    return cy_web_x.get_static_dir()


from typing import Optional, Dict



def validate_token_in_request(self, request:fastapi.Request):
    print("")
fx=validate_token_in_request

def get_fastapi_app() -> fastapi.FastAPI:
    return cy_web_x.get_fastapi_app()


def get_token_url():
    return cy_web_x.get_token_url()
import fastapi.security
def auth_type(auth_type:typing.Union[fastapi.security.OAuth2PasswordBearer,fastapi.security.OAuth2AuthorizationCodeBearer]):
    return cy_web_x.auth_type(auth_type)
def model(all_fields_are_optional:bool=False):
    return cy_web_x.model(all_fields_are_optional)

def cache_content(dir:str,file_name:str,data:bytes):
    return cy_web_x.cache_content(dir,file_name=file_name,content=data)
def cache_content_check(dir, file_path):
    return cy_web_x.cache_content_check(dir, file_path)