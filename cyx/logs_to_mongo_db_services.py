import datetime

from cyx.repository import Repository
import functools


class LogsToMongoDbService:
    @functools.cache
    def get_pod_name(self):
        f = open('/etc/hostname')
        pod_name = f.read()
        f.close()
        full_pod_name = pod_name.lstrip('\n').rstrip('\n')
        items = full_pod_name.split('-')
        if len(items) > 2:
            pod_name = "-".join(items[:-2])
        else:
            pod_name = full_pod_name
        return pod_name

    async def log_async(self, error_content):
        await Repository.lv_files_sys_logs.app("admin").context.insert_one_async(
            Repository.lv_files_sys_logs.fields.LogOn << datetime.datetime.utcnow(),
            Repository.lv_files_sys_logs.fields.ErrorContent << error_content,
            Repository.lv_files_sys_logs.fields.PodId << self.get_pod_name()
        )
