class ShareStorageService:
    """
    For multi-app system like microservice or something has the same, such as Containers in Docker or Pod in K8S.
    Every app or microservice need a common storage call share-storage.
    Share-Storage point to a certain location in a PC, EC2 or event a worker in K8S
    -------------------------------------------\n
    Đối với hệ thống đa ứng dụng như microservice hoặc thứ gì đó tương tự, chẳng hạn như Container trong Docker hoặc Pod trong K8S.
    Mọi ứng dụng hoặc vi dịch vụ đều cần một bộ nhớ chia sẻ cuộc gọi lưu trữ chung.
    Share-Storage trỏ đến một vị trí nhất định trong PC, EC2 hoặc sự kiện worker trong K8S
    """

    def __init__(self):
        from cyx.common import config
        import pathlib
        import os
        self.config = config
        self.__shared_storage__ = None
        self.__app_dir__ = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.__shared_storage__ = self.config.shared_storage
        if self.__shared_storage__[0:2] == "./":
            self.__shared_storage__ = os.path.abspath(
                os.path.join(self.__app_dir__, self.__shared_storage__[2:])
            )
        self.__share_location_file_processing__ = os.path.abspath(
            os.path.join(self.__shared_storage__, "tmp-file-processing","sync")
        )
        self.__share_location_file_processing_class__ = os.path.abspath(
            os.path.join(self.__shared_storage__, "tmp-file-processing", "tmp")
        )
        if not os.path.isdir(self.__share_location_file_processing__):
            os.makedirs(self.__share_location_file_processing__, exist_ok=True)

    def get_root(self) -> str:
        """
        Get root absolute path to Shared-Storage
        Configuration of root Share-Storage in config.yml, seeking to shared_storage
        If shared_storage start with "./" that means   shared_storage locate in App-Dir
        --------------------
        Nhận đường dẫn gốc tuyệt đối đến Shared-Storage
        Cấu hình của Share-Storage gốc trong config.yml, tìm đến shared_storage
        Nếu shared_storage bắt đầu bằng "./", điều đó có nghĩa là shared_storage nằm trong App-Dir
        :return:
        """
        import os
        return self.__shared_storage__

    def get_share_location_file_processing(self) -> str:
        """
        When sub-app, microservice, Container or Pod is in their process with file.
        They will locate to Share-Location to get, create or update content of file in Share-Location.
        Use this Function get runtime Share-Location
        --------------------------------------------------- \n
        Khi ứng dụng phụ, microservice, Container hoặc Pod đang xử lý tệp.
        sub-app, microservice, Container hay Pod sẽ định vị đến Share-Location để lấy, tạo hoặc cập nhật nội dung của tệp trong Share-Location.
        Sử dụng Chức năng này để có được vị trí chia sẻ thời gian chạy
        :return:
        """
        return self.__share_location_file_processing__

    def get_temp_dir(self, cls):
        """
        Get temp directory for File-Processing-Class. When class create file.
        They need create file in a manage-location.
        Manage-location  is a sub folder in Share-Location-File-Processing
        Manage-location for Class is a combination of Share-Location-File-Processing, Class-Module and Class-Name
        Example:
            Share-Location-File-Processing = 'app/share'
            Class-Module ='files'
            Class-Name = 'ImageService'
            get_temp_dir will return 'app/share/files/ImageService/tmp' and create app/share/files/ImageService if not exist
        ------------------------------------------- \n
        Nhận temp directory  cho File-Processing-Class. Khi Class tạo tệp.
        Class cần tạo tệp trong Manage-location.
        Manage-location là một thư mục con trong Share-Location-File-Processing
        Manage-location cho Class là sự kết hợp của Share-Location-File-Processing, Class-Module và Class-Name
        Ví dụ:
            Share-Location-File-Processing = 'app/share'
            Class-Module ='files'
            Class-Name = 'ImageService'
            get_temp_dir will return 'app/share/files/ImageService/tmp' and create app/share/files/ImageService if not exist
        :param cls:
        :return:
        """
        import os
        ret = os.path.abspath(
            os.path.join(self.__share_location_file_processing_class__, cls.__module__, cls.__name__,"tmp")
        )
        if not os.path.isdir(ret):
            os.makedirs(ret,exist_ok=True)
        return ret
    def get_logs_dir(self,cls):
        import os
        ret = os.path.abspath(
            os.path.join(self.__share_location_file_processing_class__, cls.__module__, cls.__name__, "logs")
        )
        if not os.path.isdir(ret):
            os.makedirs(ret, exist_ok=True)
        return ret