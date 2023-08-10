import typing

import fastapi

import cy_kit
import cy_xdoc.auths
import cy_web
import cy_xdoc
from cy_xdoc.controllers.models.files import FileUploadRegisterInfo
@cy_web.hanlder(method="post",path="{app_name}/files")
def get_list_of_files(

        app_name:str,
        PageSize:int,PageIndex:int,
        FieldSearch: typing.Optional[str],
        ValueSearch: typing.Optional[str],
        token=fastapi.Depends(cy_xdoc.auths.Authenticate))->typing.List[FileUploadRegisterInfo]:
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    from cy_xdoc.services.files import FileServices
    file_service = cy_kit.single(FileServices)
    items = file_service.get_list(
        app_name=app_name,
        root_url=cy_web.get_host_url(),
        page_size=PageSize,
        page_index=PageIndex,
        field_search=FieldSearch,
        value_search=ValueSearch

    )
    for x in items:
        yield x.to_pydantic()
