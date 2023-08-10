import fastapi
import cy_xdoc.auths
import cy_kit,cy_docs,cy_xdoc,cy_web
import cy_xdoc.services.files
@cy_web.hanlder(method="post",path="{app_name}/files/delete")
def files_delete(app_name:str, UploadId:str,token = fastapi.Depends(cy_xdoc.auths.Authenticate)):
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    file_service = cy_kit.single(cy_xdoc.services.files.FileServices)
    file_service.remove_upload(app_name=app_name, upload_id=UploadId)
    return {}

