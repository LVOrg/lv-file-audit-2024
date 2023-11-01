import pathlib

working_dir = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(working_dir)
sys.path.append("/app")
import cy_kit
from cyx.common.file_storage_mongodb import MongoDbFileStorage,MongoDbFileService
from cy_hybrid.file_storage import HybridFileStorage
cy_kit.config_provider(
    from_class=MongoDbFileService,
    implement_class=HybridFileStorage

)
fs = cy_kit.singleton(MongoDbFileStorage)
print(cy_kit.get_runtime_type(fs))