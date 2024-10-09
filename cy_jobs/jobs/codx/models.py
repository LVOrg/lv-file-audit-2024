import cy_docs
import typing
import datetime
@cy_docs.define("DM_FileInfo", uniques=[], indexes=["UploadId","CreatedOn","FileName","FolderPath","ObjectID"])
class Codx_DM_FileInfo:
    ImportFrom: typing.Optional[str]  #filter 'mysql'
    UploadId: typing.Optional[str]
    FilePath_Old: typing.Optional[str]  # from customer
    PathDisk: typing.Optional[
        str]  # from lv file service api/default/file/145d866f-3823-42cc-a278-01d648121fdd/166_QD.pdf
    FileName: typing.Optional[str]
    CreatedBy: typing.Optional[str]
    FileSize: typing.Optional[int]
    Permissions: typing.Optional[dict]
    ObjectType: typing.Optional[str]
    ObjectID: typing.Optional[str]
    lv_file_services_is_update_meta_v1: typing.Optional[bool]
    CreatedOn: typing.Optional[datetime.datetime]
    FolderPath: typing.Optional[str]

@cy_docs.define("WP_Comments", uniques=[], indexes=[
    "RecID","CreatedOn","PublishOn"
])
class Codx_WP_Comments:
    RecID: typing.Optional[str]
    Content: typing.Optional[str]
    CreatedOn: datetime.datetime
    PublishOn: datetime.datetime