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
class Err:
    message: str


@cy_web.model()
class Result:
    is_ok: bool
    error: typing.Optional[Err]


@cy_web.hanlder(method="post", path="{app_name}/files/update_privileges")
def update_privileges(
        app_name: str,
        Data: typing.List[cy_xdoc.controllers.models.files_register.PrivilegesType],
        UploadIds: typing.List[str],
        token=fastapi.Depends(cy_xdoc.auths.Authenticate)) -> Result:
    """
        <p>
        <b>
            For a certain pair of Application and  Access Token<br/>
        </b>
            The API allow thou remove old list of a privileges tags and set new list of privileges (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
            <code>\n
                //Example set a new  accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
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
        ret = file_services.update_privileges(
            app_name=app_name,
            upload_id=upload_id,
            privileges=[cy_docs.DocumentObject(x) for x in Data]

        )
    return Result(is_ok=True)
