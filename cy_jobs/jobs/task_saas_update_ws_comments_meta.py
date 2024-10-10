import  sys
import pathlib
import time
import traceback




sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
import cy_kit
from cyx.repository import Repository
from cyx.common import config
import cy_docs
from icecream import ic
import cy_es
from cy_es import cy_es_manager as es_manager
import elasticsearch
from retry import retry
from cyx.text_utils.html_services import HtmlService
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
import cy_kit.design_pattern
# from cy_jobs.jobs.codx.codx_ws_comment_list import CodxWSComment
from cy_jobs.jobs.codx.repositories import CodxRepository,Codx_WP_Comments
from cy_jobs.jobs.scaner_db.scaners import Scaner,ScanEntity
@cy_kit.design_pattern.singleton()
class FixMetaData:
    html_service = cy_kit.single(HtmlService)
    logs = cy_kit.singleton(LogsToMongoDbService)
    scan_ws_comments:Scaner[Codx_WP_Comments]
    def __init__(self):
        if not hasattr(config,"version"):
            raise Exception(f"version was not found in config")
        if not hasattr(config,"app_name"):
            raise Exception(f"app_name was not found in config")
        if not hasattr(config,"db_codx"):
            print(f"warning: db_codx was not found in config use default config")
        self.scan_ws_comments=Scaner[Codx_WP_Comments](
            Codx_WP_Comments,
            CodxRepository.wp_comments,
            app_name=config.app_name,
            scan_id=type(self).__name__,
            scan_value=config.version
        )
        self.es_client = elasticsearch.Elasticsearch(
            hosts=config.elastic_search.server,
            timeout=3600,
            sniff_timeout=30
        )
    def get_comment_info(self,entity:ScanEntity):
        agg = entity.context.aggregate().match(
            self.scan_ws_comments.F.id ==entity.entity_id
        ).project(
            self.scan_ws_comments.F.CreatedOn,
            self.scan_ws_comments.F.Content,
            self.scan_ws_comments.F.RecID,
        ).limit(1)
        ic(agg)
        items = list(agg)
        if len(items) > 0:
            return items[0]
        else:
            return None
    def update_es_content(self,app_name,RecID:str,Content:str):
        es_index = f"{config.elastic_search.prefix_index}_{app_name}"
        @retry(tries=10,delay=5)
        def __update_es_content__(_RecID,_Content):
            ret = es_manager.update_or_insert_content(
                client=self.es_client,
                index=es_index,
                id= _RecID,
                content= _Content
            )
            return ret
        ret = __update_es_content__(RecID,Content)
        ic(f"update {RecID} content {Content[:10]} is {ret}")
        return ret


    def do_scan_recent(self):
        for x in self.scan_ws_comments.get_entities(self.scan_ws_comments.F.CreatedOn.desc()):
            info = self.get_comment_info(x)
            if info:
                content = info.get(self.scan_ws_comments.F.Content.__name__)
                rec_iD = info.get(self.scan_ws_comments.F.RecID.__name__)
                if content and rec_iD:
                    raw_content = self.html_service.raw(content)
                    self.update_es_content(
                        app_name=x.app_name,
                        RecID=rec_iD,
                        Content=raw_content
                    )
            x.commit()

if __name__ == "__main__":
    svc= FixMetaData()
    svc.do_scan_recent()

#81ea5bf6-b483-4ee0-89d0-102041cef38a
#http://10.96.25.76:9200//lv-codx_default/_source/81ea5bf6-b483-4ee0-89d0-102041cef38a?pretty
#curl http://10.96.25.76:9200/lv-codx_default/_source/81ea5bf6-b483-4ee0-89d0-102041cef38a?pretty
#version=v-001 app_name=all
