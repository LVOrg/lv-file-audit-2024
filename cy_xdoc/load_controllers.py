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
from cy_controllers import PagesController
from cy_controllers.apps.app_controller import AppsController
from cy_controllers.logs.logs_controller import LogsController
from cy_controllers.files.files_upload_controller import FilesUploadController
from cy_controllers.files.files_content_controller import FilesContentController
from cy_controllers.files.files_register_controller import FilesRegisterController
from cy_controllers.search.search_controller import SearchController
from cy_controllers.files.files_controllers import FilesController
from cy_controllers.files.file_privileges_controller import FilesPrivilegesController
from cy_controllers.systems.system_controllers import SystemsController
from cy_controllers.health_check.health_check_controllers import HealthCheckController
from cy_controllers.azure.token_controller import AzureController
from cy_controllers.azure.fucking_one_drive import FuckingOneDriveController
from cy_controllers.wopi.wopi_controller import WOPIController
from cy_controllers.office365.office365_controller import Office365Controller
from cy_controllers.auth.auth_controller import AuthController
from cy_controllers.files.files_source_controller import FilesSourceController
from cy_controllers.global_settings.global_settinsg_controllers import GlobalSettingsController
from cy_controllers.gemini_controller.gemini_controller import GeminiControllr
from cyx.loggers import LoggerService
import cy_kit
logger_service = cy_kit.singleton(LoggerService)
controllers_list=[
        GlobalSettingsController,
        GeminiControllr,
        HealthCheckController,
        FilesContentController,
        AppsController,
        LogsController,
        FilesUploadController,
        FilesRegisterController,
        FilesController,
        FilesPrivilegesController,
        SearchController,
        SystemsController,
        AzureController,
        FuckingOneDriveController,
        FilesSourceController,
        WOPIController,
        Office365Controller,
        AuthController,
        PagesController

    ]
def load_controller(app,host_dir):

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

            raise (e)

