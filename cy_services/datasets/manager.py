import os.path
from cy_services.base_services.base import BaseService

class DatasetManagerService(BaseService):
    def __init__(self):
        fx = self.config
        self.location="/home/vmadmin/python/v6/file-service-02/share-storage/dataset"

    def get_dataset_path(self, local_datset_name:str):
        return os.path.join(self.location,local_datset_name)