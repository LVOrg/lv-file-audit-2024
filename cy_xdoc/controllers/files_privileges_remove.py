import fastapi
import typing

import cy_docs
import cy_kit
import cy_web
import cy_xdoc.auths
import cy_xdoc.models.files
import cy_xdoc.controllers.models.files_register
import cy_xdoc.services.files


@cy_web.model()
class DataPrivileges:
    UploadId: str
    Privileges: typing.List[cy_xdoc.controllers.models.files_register.PrivilegesType]


@cy_web.model()
class AddPrivilegesErr:
    message: str


@cy_web.model()
class AddPrivilegesResult:
    is_ok: bool
    error: typing.Optional[AddPrivilegesErr]


@cy_web.hanlder(method="post", path="{app_name}/files/remove_privileges")
def remove_privileges(
        app_name: str,
        Data: typing.List[cy_xdoc.controllers.models.files_register.PrivilegesType],
        UploadIds: typing.List[str],
        token=fastapi.Depends(cy_xdoc.auths.Authenticate)) -> AddPrivilegesResult:
    """
    <p>
    <b>
        For a certain pair of Application and  Access Token<br/>
    </b>
        The API allow thou remove list of a privileges tags (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
        <code>\n
            //Example remove accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
            {
                Data: [
                            {
                                Type:'departments',
                                Values: 'accounting,hr'
                            },
                            {
                                Type:'teams',
                                Values: 'Codx,xdoC'
                            }
                        ],
                UploadIds:[1,2,3]

            }
        </code>


    </p>
    :param app_name:
    :param Data:
    :param UploadIds:
    :param token:
    :return:
    """
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    file_services = cy_kit.singleton(cy_xdoc.services.files.FileServices)
    from cy_xdoc.services.search_engine import SearchEngine
    search_engine = cy_kit.singleton(SearchEngine)

    for upload_id in UploadIds:
        ret = file_services.remove_privileges(
            app_name=app_name,
            upload_id=upload_id,
            privileges=[cy_docs.DocumentObject(x) for x in Data]

        )
    return AddPrivilegesResult(is_ok=True)
