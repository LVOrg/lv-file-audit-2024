import typing

from cyx.base import config
from jose import jwt

FILE_SERVICE_COOKIE_KEY = "cy-files-token"


class TokenService:
    def __init__(self, config=config):
        self.config = config

    def generate_token(self, app: str, username: str) -> str:
        claims = {
            "application": app,
            "username": username
        }

        # Encode the claims to a JWT token
        token = jwt.encode(claims, self.config.jwt.secret_key, algorithm=self.config.jwt.algorithm)
        return token

    def get_info_from_token(self, request) -> typing.Tuple[str, str]:
        try:
            token = request.cookies.get(FILE_SERVICE_COOKIE_KEY)
            ret = jwt.decode(token=token, algorithms=self.config.jwt.algorithm, key=self.config.jwt.secret_key)
            return ret.get("application"), ret.get("username")
        except Exception as e:
            return None, None

    def set_cookie(self, response, token: str):
        if hasattr(response, "set_cookie") and callable(getattr(response, "set_cookie")):
            response.set_cookie(FILE_SERVICE_COOKIE_KEY, token)
