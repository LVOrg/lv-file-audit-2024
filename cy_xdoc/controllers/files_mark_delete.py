import fastapi
import cy_xdoc.services.files
import cy_web
import cy_xdoc
from cy_xdoc.auths import Authenticate
import cy_xdoc.models.files
import cy_xdoc.services.search_engine
import cy_kit


@cy_web.hanlder("post", "{app_name}/files/mark_delete")
async def mark_delete(app_name: str, UploadId: str, IsDelete: bool, token=fastapi.Depends(Authenticate)):
    """
    Danh dau xoa
    :param app_name:
    :param UploadId:
    :param IsDelete: True if mark deleted False if not
    :param token:
    :return:
    """
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    file_services: cy_xdoc.services.files.FileServices = cy_kit.singleton(cy_xdoc.services.files.FileServices)
    search_services:cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(cy_xdoc.services.search_engine.SearchEngine)
    doc_context = file_services.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
    delete_item = doc_context.context @ UploadId
    if delete_item is None:
        return {}
    # gfs = db_context.get_grid_fs()
    # main_file_id = delete_item.get(Files.MainFileId.__name__)

    ret = doc_context.context.update(
        doc_context.fields.id == UploadId,
        doc_context.fields.MarkDelete <<IsDelete
    )
    search_services.mark_delete(app_name=app_name, id=UploadId, mark_delete_value=IsDelete)

    # search_engine.get_client().delete(index=fasty.configuration.search_engine.index, id=es_id)
    return dict()
