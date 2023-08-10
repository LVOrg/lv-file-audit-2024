import os.path
import pathlib

from cyx.common.base import config
import cy_kit


class BaseService:
    def __init__(self):
        self.config = config
        self.shared_storage = config.shared_storage


        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()

        if self.shared_storage[0:2] == "./":
            self.shared_storage= self.shared_storage[2:]
            self.dataset_path = os.path.abspath(
                os.path.join(self.working_dir, self.shared_storage, "dataset")
            )
        else:
            self.dataset_path = os.path.abspath(
                os.path.join(self.shared_storage, "dataset")
            )


