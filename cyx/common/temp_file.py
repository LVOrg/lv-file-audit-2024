"""
Để xử lý tệp, hãy sử dụng Disk Driver thay cho RAM.
    Vì vậy, chúng tôi cần một Thư mục tạm thời để xử lý mọi tệp
        Để có được đường dẫn gốc tuyệt đối của thư mục mẫu, bạn phải gọi:
    get_root_dir hoặc đường dẫn truy cập của thể hiện
    Làm thế nào để lớp nhận được Temp-Directory? Temp_directory đến từ đâu?
    Bạn có thể gửi 'temp_directory' qua đối số khi bắt đầu ứng dụng.
    Hoặc tạo tệp config.yml rồi thêm thuộc tính 'temp_directory' với đường dẫn đầy đủ đến
    thư mục gốc 'temp_directory'

        For file processing use Disk Driver lieu of RAM.
    So, we need a Temp-Directory for any file processing
        In order to get absolute root path of template directory, thou must call:
    get_root_dir or access path of the instance
    How dose the class get Temp-Directory? Where did Temp_directory come from?
    Thou could send 'temp_directory' via argument when start application.
    Or create config.yml file then add 'temp_directory' property with full path to
    root 'temp_directory'
    -------
    於文件處理，對使用磁盤驅動程序代替 RAM。
    所以，我們需要一個臨時目錄來處理任何文件
    為了處理文件，使用磁盤驅動程序而不是 RAM。
    所以我們需要一個臨時目錄來處理任何文件
        要獲取模板目錄的絕對根路徑，您必須調用：
    get_root_dir 或實例訪問路徑
        班級如何獲得臨時目錄？ Temp_directory 是從哪裡來的？
        您可以在啟動應用程序時通過參數發送“temp_directory”。
        或者創建 config.yml 文件，然後添加帶有完整路徑的“temp_directory”屬性
        根“temp_directory”
"""
import asyncio
import os
import pathlib
import shutil
import typing

import gridfs.errors

import cy_kit
import cyx.common
from cyx.common import config
from cyx.loggers import LoggerService
from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
from cy_xdoc.services.files import FileServices
from cyx.common.share_storage import ShareStorageService
class TempFiles:
    """
        Để xử lý tệp, hãy sử dụng Disk Driver thay cho RAM.
    Vì vậy, chúng tôi cần một Thư mục tạm thời để xử lý mọi tệp
        Để có được đường dẫn gốc tuyệt đối của thư mục mẫu, bạn phải gọi:
    get_root_dir hoặc đường dẫn truy cập của thể hiện
    Làm thế nào để lớp nhận được Temp-Directory? Temp_directory đến từ đâu?
    Bạn có thể gửi 'temp_directory' qua đối số khi bắt đầu ứng dụng.
    Hoặc tạo tệp config.yml rồi thêm thuộc tính 'temp_directory' với đường dẫn đầy đủ đến
    thư mục gốc 'temp_directory'

        For file processing use Disk Driver lieu of RAM.
    So, we need a Temp-Directory for any file processing
        In order to get absolute root path of template directory, thou must call:
    get_root_dir or access path of the instance
    How dose the class get Temp-Directory? Where did Temp_directory come from?
    Thou could send 'temp_directory' via argument when start application.
    Or create config.yml file then add 'temp_directory' property with full path to
    root 'temp_directory'
    -------
    於文件處理，對使用磁盤驅動程序代替 RAM。
    所以，我們需要一個臨時目錄來處理任何文件
    為了處理文件，使用磁盤驅動程序而不是 RAM。
    所以我們需要一個臨時目錄來處理任何文件
        要獲取模板目錄的絕對根路徑，您必須調用：
    get_root_dir 或實例訪問路徑
        班級如何獲得臨時目錄？ Temp_directory 是從哪裡來的？
        您可以在啟動應用程序時通過參數發送“temp_directory”。
        或者創建 config.yml 文件，然後添加帶有完整路徑的“temp_directory”屬性
        根“temp_directory”
    """

    def __init__(self,logger = cy_kit.singleton(LoggerService)):
        self.logger = logger
        self.share_storage_service = cy_kit.singleton(ShareStorageService)
        self.__tem_path__  = self.share_storage_service.get_share_location_file_processing()
        self.file_storage = cy_kit.singleton(MongoDbFileService)
        self.files_services = cy_kit.singleton(FileServices)
        self.config = cyx.common.config
        # if self.config.get("temp_directory") is None or self.config.get("temp_directory") == '':
        #     self.__is_use__ = False
        #     print(f" warning temp_directory was not set")
        #     return
        # self.__tem_path__: str = self.config.temp_directory
        # if self.__tem_path__.startswith("./"):
        #     self.__tem_path__ = os.path.abspath(
        #         os.path.join(pathlib.Path(__file__).parent.parent.parent.__str__(), self.__tem_path__[2:]))
        #     if not os.path.isdir(self.__tem_path__):
        #         os.makedirs(self.__tem_path__, exist_ok=True)
        self.__is_use__ = True

    @property
    def is_use(self) -> bool:
        return self.__is_use__

    @property
    def path(self):
        """
        The root directory for any file processing, properly, somehow in subdirectory was belonged to root
        任何文件處理的根目錄，正確地，子目錄中的某種方式屬於根目錄
        """
        return self.__tem_path__
    async def push_async(self, upload_id: str, app_name: str, file_ext: str, content: bytes):
        return self.push(
            upload_id=upload_id,
            app_name = app_name,
            file_ext = file_ext,
            content = content
        )
    def push(self, upload_id: str, app_name: str, file_ext: str, content: bytes,sync_file_if_not_exit=True):
        """
        Create or append content to file
        The method will automatically create a sub folder in root folder (thou could get infor of
        root folder by call 'get_root_dir' ).
        創建或附加內容到文件
        該方法將自動在根文件夾中創建一個子文件夾（您可以獲得信息
        通過調用 'get_root_dir' 的根文件夾）。

        :param upload_id: filename only will be created
        :param app_name: subdirectory store file will be created
        :param file_ext: file extension
        :param content: binary content will be added
        :return:
        """
        full_path = self.get_path(app_name, upload_id, file_ext,sync_file_if_not_exit)
        print(f"Save file to {full_path}")
        if not os.path.isfile(full_path):
            with open(full_path, "wb") as f:
                f.write(content)
        else:
            with open(full_path, "ab") as f:
                f.write(content)

    def get_root_dir(self) -> str:
        """
        get temporary root directory
        :return:
        """
        return self.__tem_path__

    def get_path(self, app_name, upload_id, file_ext,file_id: str,sync_file_if_not_exit=True) -> typing.Optional[str]:
        """
        Get Full path file in tenant with root temporary directory in get_root_dir()
        Example: get_path( app_name ='my-app',upload_id='123',file_ext='txt')
        will return /app/temp/my-app/123.txt if get_root_dir() return /app/temp

        Note: The method also check if file is exist or not. If the file is not exist the method try get real file from MongoDb
        Lưu ý: Method này cũng kiểm tra xem tệp có tồn tại hay không. Nếu tệp không tồn tại, Method lấy tệp thực từ MongoDb

        :param app_name:
        :param upload_id:
        :param file_ext:
        :return:
        """
        if isinstance(file_id, str) and file_id.startswith("local://"):

            full_file_path = file_id[len("local://"):]
            if not hasattr(config, "file_storage_path"):
                self.logger.error(Exception("It look like you forget set config.file_storage_path"))
            full_file_path = os.path.join(config.file_storage_path, full_file_path)
            if not os.path.isfile(full_file_path):
                data_item = self.files_services.get_upload_register_with_cache(
                     app_name=app_name,
                        upload_id=upload_id
                )
                if data_item is None:
                    return  None
                if not  data_item.MainFileId.startswith("local://"):
                    return data_item.MainFileId
            return full_file_path


        import gridfs.errors
        app_dir = os.path.join(self.__tem_path__, app_name)
        if not os.path.isdir(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        ret = os.path.join(app_dir, f"{upload_id}.{file_ext}")
        if not os.path.isfile(ret) and sync_file_if_not_exit:

            """
            if file is not exist in temp folder
            get it from Mongodb
            """
            self.logger.info(f"{ret} was not found")
            self.logger.info(f"try sync {ret} from server")
            try:
                fs = self.files_services.get_main_file_of_upload(
                    app_name=app_name,
                    upload_id=upload_id
                )
                if fs is not None:
                    with open(ret, 'wb') as f:
                        import inspect
                        if inspect.iscoroutinefunction(fs.read):
                            data = asyncio.run(fs.read(fs.get_size()))
                        else:
                            data = fs.read(fs.get_size())
                        f.write(data)
            except gridfs.errors.CorruptGridFile as e:
                self.logger.info(f"try sync {ret} from server was fail")
                self.logger.error(e)
                return None
        self.logger.info(f"Finish sync {ret} from server")
        return ret

    def move_file(self, from_file: str, app_name: str, sub_dir: str):
        app_dir = os.path.join(self.__tem_path__, app_name)
        if not os.path.isdir(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        full_sub_dir = os.path.join(app_dir, sub_dir)
        if not os.path.isdir(full_sub_dir):
            os.makedirs(full_sub_dir, exist_ok=True)
        file_name = pathlib.Path(from_file).name
        # file_ext = os.path.splitext(file_name)[1]
        ret = os.path.join(full_sub_dir, f"{file_name}")
        shutil.move(
            src=from_file,
            dst=ret
        )
        return ret
