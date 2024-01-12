from cyx.common.mongo_db_services import RepositoryContext
import cy_kit
from cy_xdoc.models.apps import App
from cy_xdoc.models.files import DocUploadRegister


class Repository:
    apps = RepositoryContext[App](App)
    files = RepositoryContext[DocUploadRegister](DocUploadRegister)
