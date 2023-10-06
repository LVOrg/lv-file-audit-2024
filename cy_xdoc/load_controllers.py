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
from cy_controllers.files.files_controller import FilesController
from cy_controllers.files.files_content_controller import FilesContentController
from cy_controllers.files.files_register_controller import FilesRegisterController
from cyx.loggers import LoggerService
import cy_kit
logger_service = cy_kit.singleton(LoggerService)
controllers_list=[
        FilesContentController,
        AppsController,
        LogsController,
        FilesController,
        FilesRegisterController,
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

