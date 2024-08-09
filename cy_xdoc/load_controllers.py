from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    UploadFile,
    Form, File
)
from cy_controllers.notebook.notebook_controller import NoteBookController
from cy_controllers.pages.home import PagesController,RootPagesController
from cy_controllers.apps.app_controller import AppsController
from cy_controllers.logs.logs_controller import LogsController
from cy_controllers.files.files_upload_controller import FilesUploadController
from cy_controllers.files.files_content_controller import FilesContentController
from cy_controllers.files.files_content_controler_new import FilesContentControllerNew
from cy_controllers.files.files_register_controller import FilesRegisterController
from cy_controllers.search.search_controller import SearchController
from cy_controllers.files.files_controllers import FilesController
from cy_controllers.files.file_privileges_controller import FilesPrivilegesController
from cy_controllers.systems.system_controllers import SystemsController
from cy_controllers.health_check.health_check_controllers import HealthCheckController
# from cy_controllers.azure.token_controller import AzureController
# from cy_controllers.wopi.wopi_controller import WOPIController
# from cy_controllers.office365_delete.office365_controller import Office365Controller
from cy_controllers.auth.auth_controller import AuthController
from cy_controllers.files.files_source_controller import FilesSourceController
from cy_controllers.global_settings.global_settinsg_controllers import GlobalSettingsController

from cy_controllers.files.file_local_controller import FilesLocalController
from cyx.loggers import LoggerService
from cy_controllers.google.auth_controller import GoogleController
from cy_controllers.google.google_settings_controller import GoogleSettingsController
from cy_controllers.ms.ms_controller_auth import MSAuth
from cy_controllers.ms.settings import MSSettings
from cy_controllers.cloud.mails import CloudMailController
from cy_controllers.cloud.drivers import CloudDriveController
from cy_controllers.files.files_register_controller_new import FilesRegisterControllerNew
from cy_controllers.files.files_upload_controller_new import FilesUploadControllerNew
import cy_kit
logger_service = cy_kit.singleton(LoggerService)
controllers_list=[
        GlobalSettingsController,
        HealthCheckController,
        # FilesContentControllerNew,
        FilesContentController,
        AppsController,
        LogsController,
        FilesUploadController,
        FilesUploadControllerNew,
        FilesRegisterController,
        FilesRegisterControllerNew,
        FilesController,
        FilesPrivilegesController,
        SearchController,
        SystemsController,

        FilesSourceController,
        AuthController,

        GoogleController,
        GoogleSettingsController,
        MSAuth,
        MSSettings,
        CloudMailController,
        FilesLocalController,
        CloudDriveController

    ]

def load_controller(app,host_dir):
    global controllers_list
    controllers_list += [NoteBookController,RootPagesController,PagesController]
    for fx in controllers_list:
        try:
            app.include_router(
                prefix=host_dir,
                router=fx.router()
            )
        except Exception as e:
            logger_service.error(e,more_info=dict(
                controller = fx.__name__
            ))
            print(f"error load controller {fx}")


