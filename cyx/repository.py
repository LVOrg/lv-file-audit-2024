from cyx.common.mongo_db_services import RepositoryContext
import cy_kit
from cy_xdoc.models.apps import App, CloudPathTrack
from cy_xdoc.models.files import DocUploadRegister, ContentHistory, DocLocalShareInfo
from cy_xdoc.models.settings import GlobalSettings
from cy_xdoc.models.files import GoogleFolderMappings, CloudFileSync


class Repository:
    apps = RepositoryContext[App](App)
    files = RepositoryContext[DocUploadRegister](DocUploadRegister)
    contents = RepositoryContext[ContentHistory](ContentHistory)
    global_settings = RepositoryContext[GlobalSettings](GlobalSettings)
    doc_local_share_info = RepositoryContext[DocLocalShareInfo](DocLocalShareInfo)
    google_folders = RepositoryContext[GoogleFolderMappings](GoogleFolderMappings)
    cloud_file_sync = RepositoryContext[CloudFileSync](CloudFileSync)
    cloud_path_track = RepositoryContext[CloudPathTrack](CloudPathTrack)
