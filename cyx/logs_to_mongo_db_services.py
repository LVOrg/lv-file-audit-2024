import datetime
import sys

from cyx.repository import Repository
import functools
if hasattr(functools,"lru_cache"):
    def ft_cache(*args,**kwargs):
        return functools.lru_cache(maxsize = 128)(*args,**kwargs)
else:
    from functools import cache as ft_cache
import socket
class LogsToMongoDbService:
    @ft_cache
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

    @ft_cache
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
            Repository.lv_files_sys_logs.fields.LogOn << datetime.datetime.now(datetime.UTC),
            Repository.lv_files_sys_logs.fields.ErrorContent << error_content,
            Repository.lv_files_sys_logs.fields.PodId << self.get_pod_name(),
            Repository.lv_files_sys_logs.fields.Url << url,
            Repository.lv_files_sys_logs.fields.WorkerIP <<self.get_host_ip()
        )

    def log(self, error_content, url):
        def run_in_thead():
            if hasattr(datetime,"UTC"):
                log_on = datetime.datetime.now(datetime.UTC)
            else:
                log_on = datetime.datetime.utcnow()
            Repository.lv_files_sys_logs.app("admin").context.insert_one(
                Repository.lv_files_sys_logs.fields.LogOn << log_on,
                Repository.lv_files_sys_logs.fields.ErrorContent << error_content,
                Repository.lv_files_sys_logs.fields.PodId << self.get_pod_name(),
                Repository.lv_files_sys_logs.fields.Url << url,
                Repository.lv_files_sys_logs.fields.WorkerIP << self.get_host_ip()
            )
        import threading
        threading.Thread(target=run_in_thead).start()
