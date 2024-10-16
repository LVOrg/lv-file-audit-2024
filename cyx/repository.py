import datetime

from cyx.common.mongo_db_services import RepositoryContext
from cy_controllers.models.apps import AppInfo

from cyx.db_models.apps import App, CloudPathTrack
from cyx.db_models.files import (DocUploadRegister,
                                  ContentHistory,
                                  DocLocalShareInfo,
                                  Codx_DM_FileInfo,
                                  lv_file_sync_report,
                                  lv_file_sync_logs,
                                  LVFileContentProcessReport,
                                  GoogleFolderMappings,
                                 CloudFileSync,
                                DuplicateFileHistory,
                                Codx_WP_Comments

                                  )
from cy_controllers.models.settings import GlobalSettings
from cyx.loggers import sys_app_logs
import cy_docs


@cy_docs.define(
    name="lv-file-logs",
    uniques=[],
    indexes=[
        "PodId",
        "LogOn"
    ]

)
class LVFileSysLogs:
    PodId: str
    LogOn: datetime.datetime
    ErrorContent: str
    Url: str
    WorkerIP:str


class Repository:
    apps = RepositoryContext[App](App)
    files = RepositoryContext[DocUploadRegister](DocUploadRegister)
    contents = RepositoryContext[ContentHistory](ContentHistory)
    global_settings = RepositoryContext[GlobalSettings](GlobalSettings)
    doc_local_share_info = RepositoryContext[DocLocalShareInfo](DocLocalShareInfo)
    google_folders = RepositoryContext[GoogleFolderMappings](GoogleFolderMappings)
    cloud_file_sync = RepositoryContext[CloudFileSync](CloudFileSync)
    cloud_path_track = RepositoryContext[CloudPathTrack](CloudPathTrack)
    sys_app_logs_coll = RepositoryContext[sys_app_logs](sys_app_logs)
    codx_dm_file_info = RepositoryContext[Codx_DM_FileInfo](Codx_DM_FileInfo)
    codx_wp_comments = RepositoryContext[Codx_WP_Comments](Codx_WP_Comments)

    lv_file_sync_report = RepositoryContext[lv_file_sync_report](lv_file_sync_report)
    lv_file_sync_logs = RepositoryContext[lv_file_sync_logs](lv_file_sync_logs)
    lv_files_sys_logs = RepositoryContext[LVFileSysLogs](LVFileSysLogs)
    lv_file_content_process_report = RepositoryContext[LVFileContentProcessReport](LVFileContentProcessReport)
    duplicate_file_history = RepositoryContext[DuplicateFileHistory](DuplicateFileHistory)
