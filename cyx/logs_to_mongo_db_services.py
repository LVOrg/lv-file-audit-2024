import datetime

from cyx.repository import Repository
import functools

import socket
class LogsToMongoDbService:
    @functools.cache
    def get_pod_name(self):
        f = open('/etc/hostname')
        pod_name = f.read()
        f.close()
        full_pod_name = pod_name.lstrip('\n').rstrip('\n')
        return full_pod_name

    @functools.cache
    def get_host_ip(self):
        f = open('/etc/hostname')
        pod_name = f.read()
        f.close()
        hostname = socket.gethostname()
        host_ip = socket.gethostbyname(pod_name)
        return host_ip
    async def log_async(self, error_content,url):
        await Repository.lv_files_sys_logs.app("admin").context.insert_one_async(
            Repository.lv_files_sys_logs.fields.LogOn << datetime.datetime.utcnow(),
            Repository.lv_files_sys_logs.fields.ErrorContent << error_content,
            Repository.lv_files_sys_logs.fields.PodId << self.get_pod_name(),
            Repository.lv_files_sys_logs.fields.Url << url,
            Repository.lv_files_sys_logs.fields.WorkerIP <<self.get_host_ip()
        )
