import datetime
import uuid

import cy_kit

from cyx.common.base import DbConnect
from cy_xdoc.models.users import User
from cy_xdoc.models.sso import SSO
from passlib.context import CryptContext


class AccountService:
    def __init__(self, db_connect:DbConnect=cy_kit.inject(DbConnect)):
        self.db_connect = db_connect
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, hash_data: str):
        return self.pwd_context.hash(hash_data)

    def validate(self, app_name, username: str, password: str):
        doc=self.db_connect.db(app_name).doc(User)
        user = doc.context @ (doc.fields.UsernameLowerCase == username.lower())
        if user is None:
            return False
        if not self.verify_password(
                plain_password=username.lower() + "/" + password,
                hashed_password=user.HashPassword
        ):
            return False
        else:
            return True
        if user is None:
            return False
        else:
            return True

    def create_sso_id(self, app_name: str, token: str, return_url: str):
        doc = self.db_connect.db('admin').doc(SSO)
        sso_id = str(uuid.uuid4())
        ret = doc.context.insert_one(
            doc.fields.SSOID << sso_id,
            doc.fields.ReturnUrlAfterSignIn << return_url,
            doc.fields.CreatedOn << datetime.datetime.utcnow(),
            doc.fields.Token << token,

        )
        return sso_id

    def get_sso_login(self,id:str):
        doc = self.db_connect.db('admin').doc(SSO)
        ret =doc.context @ (doc.fields.SSOID==id)
        return ret


    def create_default_user(self):
        doc= self.db_connect.db('admin').doc(User)
        root_user =doc.context @ (doc.fields.UsernameLowerCase=="root")
        if root_user:
            return root_user
        self.create_user(
            app_name="admin",
            username="root",
            password="root",
            is_sys_admin= True,
            email=None

        )
    def create_user(self, app_name:str, username:str,is_sys_admin:bool,email:str, password:str):
        hash_password = self.get_password_hash(f"{username.lower()}/{password}")
        doc= self.db_connect.db(app_name).doc(User)
        ret =doc.context.insert_one(
            doc.fields.UsernameLowerCase<<username.lower(),
            doc.fields.CreatedOn<<datetime.datetime.utcnow(),
            doc.fields.HashPassword<<hash_password,
            doc.fields.Username <<username,
            doc.fields.IsLocked <<False,
            doc.fields.IsSysAdmin<<is_sys_admin,
            doc.fields.Email <<email
        )
        return ret