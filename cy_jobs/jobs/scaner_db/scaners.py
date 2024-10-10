
"""
The framework structure for Mongodb collection scaner
Some missing data in Elastic Search or in Lv file mongodb need to be filled
The missing data will get from other database such sa Mongodb Codx or even in Codx PostgreSQL

Cấu trúc khung cho trình quét bộ sưu tập Mongodb
Một số dữ liệu còn thiếu trong Elastic Search hoặc trong file Lv mongodb cần được điền
Dữ liệu bị thiếu sẽ lấy từ cơ sở dữ liệu khác như Mongodb Codx hoặc thậm chí trong Codx PostgreSQL

"""
import typing

from datetime import datetime

import cy_docs
import pymongo.results

T = typing.TypeVar("T")
from cyx.repository import Repository
from cyx.common.mongo_db_services import RepositoryContext
import cy_kit.design_pattern
from pymongo import MongoClient
from cyx.common import config
import pymongo.results
import pymongo.errors
import sys
import functools
if hasattr(functools,"cache"):
    from functools import cache as ft_cache
else:

    def ft_cache(*args,**kwargs):
        return functools.lru_cache(maxsize = 128)(*args,**kwargs)
@ft_cache
def get_pod_name():
    if sys.platform in ["win32", "win64"]:
        import platform
        return platform.node()
    else:
        f = open('/etc/hostname')
        pod_name = f.read()
        f.close()
        full_pod_name = pod_name.lstrip('\n').rstrip('\n')
        return full_pod_name
@cy_docs.define(name="ScanReport",indexes=["EntityId","EntityName","ConsumerId","AppName"],uniques=["EntityId,EntityName,ConsumerId,AppName"])
class ScanReport:
    """
    Definition of Scan Log
    Định nghĩa Nhật ký quét
    """
    EntityId:typing.Any
    """
    _id of document in Mongodb Collection 
    _id của tài liệu trong Bộ sưu tập Mongodb
    """
    EntityName: str
    """
    Collection name
    Tên bộ sưu tập
    """
    AppName:str
    """
    Tenant name
    """
    ConsumerId: str
    """
    Use to be pod name in K8s
    """
    IsError: bool
    """
    When scan dev cn do something if error please set value here
    """
    ErrorContent: str
    """
    Error content set here
    """
    StartOn: datetime
    """
    Begin scan
    """
    EndOn: datetime
    """
    End scan
    """
    ScanTimeInSecs: float
    """
    Scan time log in second format
    """
    ProcessType:str
class ScanEntity:
    """
    Scan Entity
    When Scaner document in Mongodb Collection each Item will be iterate by this instance of this class
    Khi quét tài liệu trong Bộ sưu tập Mongodb, mỗi Mục sẽ được lặp lại theo phiên bản của lớp này
    """
    context=None
    """
    Actually db_context in which dev can access to MongoDB
    Trên thực tế, bối cảnh db trong đó nhà phát triển có thể truy cập vào MongoDB
    """
    scan_id: str
    """
    Actually the pod name in k8s
    """
    scan_value: str
    """
    Every time when scan all entities the san_value must be change:
    Example: the first time scan for OCR this value should be ocr-v-01 the time scan should be ocr-v-02  
    """
    scan_field=None
    """
    This the field name will be add to MongoDB Collection with value at scan_value. That avoid duplicate scan
    Actually the mark that document was csan or  not 
    """
    entity_id=None
    """
    Map to _id of MongoDb Collection
    """
    app_name:str
    """
    Tenant name
    """
    entity_name: str
    """
    Mongodb collection in tenant db
    """
    logs : cy_docs.DbQueryableCollection[ScanReport]
    log_record_id=None
    start_on: datetime
    process_type:str
    def __repr__(self):
        return f"{self.entity_id}\t{self.scan_id}\t{self.scan_value}\t{self.app_name}"
    def commit(self)->typing.Union[pymongo.results.UpdateResult,None]:

        if self.log_record_id:
            end_on = datetime.utcnow()
            time_in_secs = (end_on-self.start_on).seconds
            self.logs.context.update(
                self.logs.fields.id ==self.log_record_id,
                self.logs.fields.EndOn << end_on,
                self.logs.fields.ScanTimeInSecs << time_in_secs
            )
        if hasattr(self.context,"update") and callable(self.context.update):
            ret:pymongo.results.UpdateResult =self.context.update(
                cy_docs.fields._id==self.entity_id,
                self.scan_field<<self.scan_value
            )
            return ret
    def error(self,error_content:str):
        if self.log_record_id:
            end_on = datetime.utcnow()
            time_in_secs = (end_on-self.start_on).seconds
            self.logs.context.update(
                self.logs.fields.id ==self.log_record_id,
                self.logs.fields.EndOn << end_on,
                self.logs.fields.ScanTimeInSecs << time_in_secs,
                self.logs.fields.ErrorContent <<error_content,
                self.logs.fields.IsError << True
            )
    def get_data(self):
        data =  self.context.find_one(
            cy_docs.fields._id==self.entity_id
        )
        return data

    def accquire_scan(self):

        try:
            self.start_on = datetime.utcnow()
            ret = self.logs.context.insert_one(
                self.logs.fields.ConsumerId << self.scan_id,
                self.logs.fields.StartOn  << datetime.utcnow(),
                self.logs.fields.EntityId << self.entity_id,
                self.logs.fields.EntityName << self.entity_name,
                self.logs.fields.AppName << self.app_name,
                self.logs.fields.ProcessType << self.process_type,
                self.logs.fields.IsError << False,
                self.logs.fields.ErrorContent << "",
                self.logs.fields.ScanTimeInSecs << 0.0
            )
            self.log_record_id= ret.inserted_id
        except pymongo.errors.DuplicateKeyError as ex:
            data_item = self.logs.context.aggregate().match(
                (self.logs.fields.ConsumerId == self.scan_id) &
                (self.logs.fields.EntityId == self.entity_id) &
                (self.logs.fields.EntityName == self.entity_name) &
                (self.logs.fields.AppName == self.app_name)
            ).project(
                cy_docs.fields.scan_id>> cy_docs.fields._id,
                cy_docs.fields.start_on >> self.logs.fields.StartOn
            ).limit(1)
            item = data_item.first_item()
            if item:
                self.log_record_id = item.get("scan_id")
                self.start_on = item.start_on
                self.logs.context.update(
                    self.logs.fields.id==self.log_record_id,
                    self.logs.fields.ConsumerId << self.scan_id,
                    self.logs.fields.StartOn << datetime.utcnow(),
                    self.logs.fields.EntityId << self.entity_id,
                    self.logs.fields.EntityName << self.entity_name,
                    self.logs.fields.AppName << self.app_name,
                    self.logs.fields.ProcessType << self.process_type,
                    self.logs.fields.IsError << False,
                    self.logs.fields.ErrorContent << "",
                    self.logs.fields.ScanTimeInSecs << 0.0
                )




@cy_kit.design_pattern.singleton()
class Filter(typing.Generic[T]):
    def __init__(self,cls_type:T):
        self.__cls__ = cls_type
    @property
    def f(self) -> T:
        return cy_docs.cy_docs_x.fields[self.__cls__]

@cy_kit.design_pattern.singleton()
class Scaner(typing.Generic[T]):
    """
    This class serve for mongodb collection scan
    The purpose of this class is help system scan a collection in Mongodb

    """
    context:RepositoryContext[T]
    """
    
    """
    scan_id: str
    """
    If the process is running in Kubernetes, the value is obtained from the Pod name in Kubernetes, instead of the PC name
    Nếu tiến trình đang chạy trong Kubernetes, giá trị được lấy từ tên Pod trong Kubernetes, thay vì tên PC
    """
    scan_value: str
    """
    Scan version
    Example the first run OCR this value is "ocr-001" the second time this value is "ocr-002"
    """
    codx_client:typing.Optional[MongoClient]
    """
    To connect to the MongoDB database in Codx, this value will be empty if Codx and LvFileDB are both part of the same MongoDB instance. 
    In the other case, the connection would be made directly to the LvFileDB database instead of Codx.
    Để kết nối với cơ sở dữ liệu MongoDB trong Codx, giá trị này sẽ trống nếu Codx và LvFileDB đều là một phần của cùng một phiên bản MongoDB. 
    Trong trường hợp khác, kết nối sẽ được thực hiện trực tiếp tới cơ sở dữ liệu LvFileDB thay vì Codx.  
    """
    filter=None
    """
    The default filter for unmarked scan entities allows you to view and manage entities that have not been marked as scanned. 
    You can modify this filter or add more criteria to customize your view
    Bộ lọc mặc định cho các thực thể quét không được đánh dấu cho phép bạn xem và quản lý các thực thể chưa được đánh dấu là đã quét. 
    Bạn có thể sửa đổi bộ lọc này hoặc thêm tiêu chí khác để tùy chỉnh chế độ xem của mình
    Default value is --<Scaner class name>--.<scan_id>!=<scan_value>
    """
    logs=cy_docs.DbQueryableCollection[ScanReport]
    def __init__(self,
                 cls_type:T,
                 context:RepositoryContext[T],
                 app_name:str,
                 scan_id:str,
                 scan_value:str):
        """
        Init new scan with Generic Type Mongodb Collection
        @param cls_type: Type of Entity map to mongodb. Entity is class with decorator cy_docs.define
        @param context: Generic db_context with cls_type
        @param app_name: db name of mongodb if this is running on single tenant (used to be use with on-premise) for saas (multi tenant) this value must be 'all'

        @param scan_value:Scan version\n Example the first run OCR this value is "ocr-001" the second time this value is "ocr-002"
        """
        self.cls_type=cls_type
        self.context = context
        self.context = context
        self.scan_id= scan_id
        self.scan_value=scan_value
        self.consumer_id = get_pod_name()
        items = self.scan_id.split(".")
        self.scan_field =getattr(getattr(getattr(cy_docs.fields,"--lv-scan_process--"),get_pod_name()),self.cls_type.__name__)
        for x in items:
            self.scan_field=getattr(self.scan_field,x)
        self.filter=(self.scan_field==None)|(self.scan_field!=self.scan_value)
        self.app_name = app_name
        self.codx_client = None
        if config.get("db_codx") and config.get("db_codx")!="":
            self.codx_client = MongoClient(config.db_codx)
        self.logs=cy_docs.DbQueryableCollection[ScanReport](ScanReport, self.context.__client__, config.admin_db_name)
    @property
    def F(self) -> T:
        return cy_docs.cy_docs_x.fields[self.cls_type]
    def get_apps(self)->typing.Iterable[str]:
        if self.app_name!="all":
            yield self.app_name
        else:
            if self.codx_client:
                list_of_db_name_in_mongo_db: typing.List[str] =self.codx_client.list_database_names()
                list_of_db_name_in_mongo_db= [x[:-5] for x in list_of_db_name_in_mongo_db if x.endswith("_Data") ]
            else:
                list_of_db_name_in_mongo_db: typing.List[str] = self.context.__client__.list_database_names()

            app_agg = Repository.apps.app("admin").context.aggregate().match(
                (Repository.apps.fields.AccessCount>0) & (Repository.apps.fields.Name!=config.admin_db_name)
            ).sort(
                Repository.apps.fields.LatestAccess.desc(),
                Repository.apps.fields.RegisteredOn.desc(),
            ).project(
                cy_docs.fields.app_name>>Repository.apps.fields.Name
            )
            lst = [x.app_name for x in list(app_agg) if x.app_name in list_of_db_name_in_mongo_db]
            for x in lst:
                yield x
    def get_entities(self,*sort:typing.Union[cy_docs.DocumentField,typing.Tuple[cy_docs.DocumentField]])->typing.Iterable[ScanEntity]:
        """
        Retrieving all entities results in an infinite iterable, meaning the process will continue indefinitely without reaching an end\n
        Việc truy xuất tất cả các thực thể dẫn đến một lần lặp vô hạn, nghĩa là quá trình sẽ tiếp tục vô thời hạn mà không kết thúc
        @param sort:
        @return:
        """

        while True:
            for app_name in self.get_apps():
                _db_context = self.context.app(app_name).context
                agg = _db_context.aggregate().match(
                    self.filter
                ).sort(*sort).project(
                    cy_docs.fields.entity_id>> cy_docs.fields._id
                ).limit(1)
                items = list(agg)
                if len(items)>0:
                    ret = ScanEntity()
                    ret.context=_db_context
                    ret.scan_value= self.scan_value
                    ret.scan_field = self.scan_field
                    ret.scan_id = self.consumer_id
                    ret.entity_id = items[0].get("entity_id")
                    ret.app_name = app_name
                    ret.entity_name = _db_context.collection.name
                    ret.logs = self.logs
                    ret.process_type = type(self).__name__
                    ret.accquire_scan()
                    yield ret



def main():
    from cyx.db_models.files import DocUploadRegister
    from cy_jobs.jobs.codx.repositories import CodxRepository,Codx_WP_Comments
    scaner_files = Scaner[DocUploadRegister](
        DocUploadRegister,
        Repository.files,
        app_name="all",
        scan_value="v-03",
        scan_id="long-test"

    )
    entities = scaner_files.get_entities(scaner_files.F.LastModifiedOn.desc(),scaner_files.F.RegisterOn.desc())
    for x in entities:
        print(x)
        x.commit()

    scan_ws_comments = Scaner[Codx_WP_Comments](
        Codx_WP_Comments,
        CodxRepository.wp_comments,
        app_name="all",
        scan_id="long-test",
        scan_value="v-01"
    )
    entities = scan_ws_comments.get_entities(scan_ws_comments.F.PublishOn.desc())
    for x in entities:
        print(x)
        data = x.get_data()
        x.commit()

if __name__ == "__main__":
    main()



