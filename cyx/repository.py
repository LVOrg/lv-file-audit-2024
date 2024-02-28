from cyx.common.mongo_db_services import RepositoryContext
import cy_kit
from cy_xdoc.models.apps import App
from cy_xdoc.models.files import DocUploadRegister, ContentHistory
from cy_xdoc.models.settings import GlobalSettings


class Repository:
    apps = RepositoryContext[App](App)
    files = RepositoryContext[DocUploadRegister](DocUploadRegister)
    contents = RepositoryContext[ContentHistory](ContentHistory)
    global_settings = RepositoryContext[GlobalSettings](GlobalSettings)
