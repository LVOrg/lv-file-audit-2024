import fastapi
import cy_web
import cy_kit
import cy_xdoc.auths
from cy_xdoc.services.files import FileServices
from cy_xdoc.controllers.models.files_register import RegisterUploadInfo, RegisterUploadInfoResult


@cy_web.hanlder("post", "{app_name}/files/register")
async def register_new_upload(app_name: str, Data: RegisterUploadInfo,
                              token=fastapi.Depends(cy_xdoc.auths.Authenticate)) -> RegisterUploadInfoResult:
    """
    <p>
    <b>
    For a certain pair of Application and  Access Token, before upload any file. Thou must call this api with post data looks like :<br>
     <code>
        {\n
           Data: { \n
                    FileName: <original client file name only when user upload>,\n
                    ChunkSizeInKB: < a certain file content will be split into many chunks, each chunk has size was limit in this argument >,\n
                    FileSize: <The real certain file size when end user upload>,\n
                    IsPublic: <true if anyone can access the content of file, false: just someone who can access the content of file with their privileges >,\n
                    ThumbConstraints: <This is an optional param, the value looks like '100,200,400,800'.
                                        The service will generate list of thumbnails in those size constraints in list of squares looks like 100x100, 200x200,400x400,800x800  >,\n
                     Privileges: <This is an optional param. This is a list of tags. Each tag is a pair of Type and Values.
                                    (   1- Type is an object type. Thou could set any text value for thy desire.
                                        2- Values is a text which describe a list of values separated by comma.
                                     )
                                    Those looks like: [
                                                            {
                                                                Type: 'departemts',
                                                                Values: 'accounting,hr'
                                                            },
                                                            ...
                                                            {
                                                                Type:'teams',
                                                                Values:'codx,sale,marketing'
                                                            },
                                                            {
                                                                Type:'position',
                                                                Values:' director, team-leader, staff'
                                                            }

                                                        ] >
                }
        }
     </code>
     </b>
    </p>
    :param app_name: Ứng dụng nào cần đăng ký Upload
    :param Data: Thông tin đăng ký Upload
    :param token:
    :return:
    """
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    file_service = cy_kit.single(FileServices)
    from cy_xdoc.services.search_engine import SearchEngine
    search_engine = cy_kit.singleton(SearchEngine)
    privileges = Data.Privileges
    ret = file_service.add_new_upload_info(
        app_name=app_name,
        chunk_size=Data.ChunkSizeInKB * 1024,
        file_size=Data.FileSize,
        client_file_name=Data.FileName,
        is_public=Data.IsPublic,
        thumbs_support=Data.ThumbConstraints,
        web_host_root_url=cy_web.get_host_url(),
        privileges_type=privileges,
        meta_data = Data.meta_data

    )
    return RegisterUploadInfoResult(Data=ret.to_pydantic())
