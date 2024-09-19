import pathlib
import sys



sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.common.mongo_db_services import MongodbService
from cyx.common import content_marterial_utils
mongodb_service = cy_kit.singleton(MongodbService)
from cy_xdoc.models.files import DocUploadRegister
ctx = mongodb_service.db("lacvietdemo").get_document_context(DocUploadRegister)


item = ctx.context.find_one(
    ctx.fields.id=="bf2aaa2c-0531-4602-b102-663e6b28cf0c"
)

is_thumbnails_able = content_marterial_utils.check_is_thumbnails_able(item)
print(item)