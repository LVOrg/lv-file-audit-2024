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
class RemakeMetaSearch:
    html_service = cy_kit.single(HtmlService)
    logs = cy_kit.singleton(LogsToMongoDbService)
    def __init__(self):
        self.app_name = config.get("app_name") or "default"
        self.codx_db = config.codx_db
        self.meta_version = config.meta_version
        self.content_vn_update_mark_field = getattr(cy_docs.fields, "content_vn_update_mark")
        self.filter = (self.content_vn_update_mark_field == None) | (self.content_vn_update_mark_field != self.meta_version)
        self.codx_ws_comments = Repository.codx_wp_comments.app(self.codx_db)
        self.time_interval = config.get("time_interval") or 5
        self.es_index = f"{config.elastic_search.prefix_index}_{self.app_name}"
        self.client = elasticsearch.Elasticsearch(
            hosts=config.elastic_search.server,
            timeout=3600,
            sniff_timeout=30
        )
        ic(self.filter)

    # def create_vn_index(self):
    #     es_manager.close_index(client=self.client, index=self.es_index)
    #     es_manager.add_bm25_similarity(client=self.client, index=self.es_index)
    #     es_manager.create_no_accent_settings(
    #         client=self.client,
    #         index=self.es_index
    #     )
    #     es_manager.create_no_accent_mapping(
    #         client=self.client,
    #         index=self.es_index,
    #         field_name="content_vn"
    #     )
    #     es_manager.open_index(client=self.client, index=index_name)



    def get_latest_codx_comment(self):
        agg = self.codx_ws_comments.context.aggregate().sort(
            self.codx_ws_comments.fields.CreatedOn.desc()
        ).match(
            self.filter
        ).project(
            self.codx_ws_comments.fields.CreatedOn,
            self.codx_ws_comments.fields.Content,
            self.codx_ws_comments.fields.RecID,
        ).limit(1)
        ic(agg)
        items = list(agg)
        if len(items)>0:
            return items[0]
        else:
            return None

    def update_es_content(self,RecID:str,Content:str):
        @retry(tries=10,delay=5)
        def __update_es_content__(_RecID,_Content):
            ret = es_manager.update_or_insert_content(
                client=self.client,
                index=self.es_index,
                id= _RecID,
                content= _Content
            )
            return ret
        ret = __update_es_content__(RecID,Content)
        ic(f"update {RecID} content {Content[:10]} is {ret}")
        return ret
    def update_status(self, RecID):
        self.codx_ws_comments.context.update(
            self.codx_ws_comments.fields.RecID== RecID,
            self.content_vn_update_mark_field << self.meta_version
        )
    def do_update_item(self):
        codx_comment_item = self.get_latest_codx_comment()
        if codx_comment_item is None:
            return
        rec_id = codx_comment_item.get("RecID")
        if not rec_id:
            return
        content = codx_comment_item.get("Content") or ""
        raw_content = self.html_service.raw(content)
        self.update_es_content(
            RecID=rec_id,
            Content=raw_content
        )
        self.update_status(
            RecID=rec_id
        )
        return rec_id

if __name__ == "__main__":
    svc= cy_kit.singleton(RemakeMetaSearch)
    while True:
        rec_id= None
        try:
            rec_id = svc.do_update_item()


        except:
            svc.logs.log(
                error_content=traceback.format_exc(),
                url=f"WS_Commments {rec_id or ''}"

            )
        finally:
            time.sleep(svc.time_interval)



#81ea5bf6-b483-4ee0-89d0-102041cef38a
#http://10.96.25.76:9200//lv-codx_default/_source/81ea5bf6-b483-4ee0-89d0-102041cef38a?pretty
#curl http://10.96.25.76:9200/lv-codx_default/_source/81ea5bf6-b483-4ee0-89d0-102041cef38a?pretty
