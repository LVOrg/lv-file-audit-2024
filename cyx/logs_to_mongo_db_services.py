import datetime
import sys

from cyx.repository import Repository
import functools

import socket
class LogsToMongoDbService:
    @functools.cache
    def get_pod_name(self):
        if sys.platform in ["win32","win64"]:
            import platform
            return platform.node()
        else:
            f = open('/etc/hostname')
            pod_name = f.read()
            f.close()
            full_pod_name = pod_name.lstrip('\n').rstrip('\n')
            return full_pod_name

    @functools.cache
    def get_host_ip(self):
        if sys.platform in ["win32","win64"]:
            import platform
            return platform.node()
        else:
            f = open('/etc/hostname')
            pod_name = f.read()
            f.close()
            hostname = socket.gethostname()
            return hostname
    async def log_async(self, error_content,url):
        await Repository.lv_files_sys_logs.app("admin").context.insert_one_async(
            Repository.lv_files_sys_logs.fields.LogOn << datetime.datetime.utcnow(),
            Repository.lv_files_sys_logs.fields.ErrorContent << error_content,
            Repository.lv_files_sys_logs.fields.PodId << self.get_pod_name(),
            Repository.lv_files_sys_logs.fields.Url << url,
            Repository.lv_files_sys_logs.fields.WorkerIP <<self.get_host_ip()
        )

    def log(self, error_content, url):
        Repository.lv_files_sys_logs.app("admin").context.insert_one(
            Repository.lv_files_sys_logs.fields.LogOn << datetime.datetime.utcnow(),
            Repository.lv_files_sys_logs.fields.ErrorContent << error_content,
            Repository.lv_files_sys_logs.fields.PodId << self.get_pod_name(),
            Repository.lv_files_sys_logs.fields.Url << url,
            Repository.lv_files_sys_logs.fields.WorkerIP << self.get_host_ip()
        )
