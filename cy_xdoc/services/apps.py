import datetime
import uuid

import cy_docs
import cy_kit
from cyx.common.base import DbConnect
from cy_xdoc.models.apps import App
import cyx.common
import cyx.common.cacher
class AppServices:

    def __init__(self,
                 db_connect=cy_kit.singleton(cyx.common.base.DbConnect),
                 cacher=cy_kit.singleton(cyx.common.cacher.CacherService)
                 ):
        self.db_connect=db_connect
        self.config = cyx.common.config
        self.admin_db = self.config.admin_db_name
        self.cacher = cacher
        self.cache_type = f"{App.__module__}.{App.__name__}"
    def get_list(self, app_name: str):
        docs = self.db_connect.db(app_name).doc(App)

        ret = docs.context.aggregate().project(
            cy_docs.fields.AppId >> docs.fields._id ,
            docs.fields.name,
            docs.fields.description,
            docs.fields.domain,
            docs.fields.login_url,
            docs.fields.return_url_afterSignIn,
            docs.fields.LatestAccess,
            docs.fields.AccessCount,
            docs.fields.RegisteredOn

        ).sort(
            docs.fields.LatestAccess.desc(),
            docs.fields.Name.asc(),
            docs.fields.RegisteredOn.desc()
        )
        return ret

    def get_item(self, app_name, app_get):
        docs = self.db_connect.db(app_name).doc(App)
        return docs.context.aggregate().project(
            cy_docs.fields.AppId >> docs.fields.Id ,
            docs.fields.Name,
            docs.fields.description,
            docs.fields.domain,
            docs.fields.login_url,
            docs.fields.return_url_afterSignIn,
            docs.fields.ReturnSegmentKey

        ).match(docs.fields.Name == app_get).first_item()
    def get_item_with_cache(self, app_name):
        ret = self.cacher.get_by_key(self.cache_type,app_name)
        if ret:
            return ret
        else:
            ret= self.get_item(app_name='admin',app_get=app_name)
            self.cacher.add_to_cache(self.cache_type,app_name,ret)
            return ret

    def create(self,
               Name: str,
               Domain: str,
               Description: str=None,
               LoginUrl: str=None,
               ReturnUrlAfterSignIn: str=None,
               UserName: str=None,
               Password: str=None,
               ReturnSegmentKey:str=None):
        docs = self.db_connect.db('admin').doc(App)
        doc = docs.fields
        app_id = str(uuid.uuid4())
        secret_key = str(uuid.uuid4())
        docs.context.insert_one(
            doc.Id << app_id,
            doc.Name << Name,
            doc.ReturnUrlAfterSignIn << ReturnUrlAfterSignIn,
            doc.Domain << Domain,
            doc.LoginUrl << LoginUrl,
            doc.Description << Description,
            doc.Username << UserName,
            doc.Password << Password,
            doc.SecretKey << secret_key,
            doc.RegisteredOn << datetime.datetime.utcnow(),
            doc.ReturnSegmentKey<<ReturnSegmentKey

        )

        ret = cy_docs.DocumentObject(
            AppId=app_id,
            Name=Name,
            ReturnUrlAfterSignIn=ReturnUrlAfterSignIn,
            Domain=Domain,
            LoginUrl=LoginUrl,
            Description=Description,
            Username = UserName,
            SecretKey = secret_key,
            RegisteredOn= datetime.datetime.utcnow()
        )
        return ret
    def update(self,
               AppId: str,
               Description: str,
               Domain: str,
               LoginUrl: str,
               ReturnUrlAfterSignIn: str,
               ReturnSegmentKey:str,
               UserName: str,
               Password: str):
        docs = self.db_connect.db('admin').doc(App)
        doc = docs.fields

        ret = docs.context.update(
            doc.Id == AppId,
            doc.ReturnUrlAfterSignIn << ReturnUrlAfterSignIn,
            doc.Domain << Domain,
            doc.LoginUrl << LoginUrl,
            doc.Description << Description,


            doc.ModifiedOn << datetime.datetime.utcnow(),
            doc.ReturnSegmentKey<<ReturnSegmentKey

        )
        ret_app = docs.context.find_one(doc.Id == AppId)
        self.cacher.remove_from_cache(self.cache_type,ret_app.Name)


        return ret_app
    def create_default_app(self,domain:str,login_url:str,return_url_after_sign_in:str):
        document=self.db_connect.db('admin').doc(App)
        default_amdin_db = self.admin_db
        application = document.context @ (document.fields.Name==default_amdin_db)
        if application is None:
            document.context.insert_one(
                document.fields.Name<<default_amdin_db,
                document.fields.Domain<<domain,
                document.fields.RegisteredOn<<datetime.datetime.utcnow(),
                document.fields.LoginUrl<<login_url,
                document.fields.ReturnUrlAfterSignIn<<return_url_after_sign_in
            )



