"""
This library has only one Class SearchEngine \n
 File-Service use Elasticsearch document with below struct: \n
        {
            content:"..." //  text of any document will store here văn bản của bất kỳ tài liệu sẽ lưu trữ ở đây \n
            data_item: Dictionary // meta info when user upload or create blog thông tin meta khi người dùng tải lên hoặc tạo blog
            meta_info: //the data come from another app which use File-Service like microservice dữ liệu đến từ một ứng dụng khác sử dụng Dịch vụ tệp như microservice
            meta_data: // the information was generated by OS or software when file create thông tin được tạo bởi hệ điều hành hoặc phần mềm khi tệp tạo hoặc


        }
"""
import asyncio
import datetime
import pathlib
import time
import typing

import elasticsearch

import cy_docs
import cy_kit
import cy_es
import cyx.common
from cy_xdoc.services.text_procesors import TextProcessService
from cy_xdoc.services.file_content_extractors import FileContentExtractorService
# from cyx.rdr_segmenter.segmenter_services import VnSegmenterService
# import cyx.vn_predictor
from cyx.loggers import LoggerService


class SearchEngine:
    """
    This library has only one Class SearchEngine \n
    File-Service use Elasticsearch document with below struct: \n
        {
            content:"..." //  text of any document will store here văn bản của bất kỳ tài liệu sẽ lưu trữ ở đây \n
            data_item: Dictionary // meta info when user upload or create blog thông tin meta khi người dùng tải lên hoặc tạo blog
            meta_info: //the data come from another app which use File-Service like microservice dữ liệu đến từ một ứng dụng khác sử dụng Dịch vụ tệp như microservice
            meta_data: // the information was generated by OS or software when file create thông tin được tạo bởi hệ điều hành hoặc phần mềm khi tệp tạo hoặc


        }

    """

    def __init__(self,
                 text_process_service: TextProcessService = cy_kit.singleton(TextProcessService),
                 file_content_extractor_service: FileContentExtractorService = cy_kit.singleton(
                     FileContentExtractorService
                 ),
                 # vn=cy_kit.singleton(VnSegmenterService),
                 # vn_predictor=cy_kit.singleton(cyx.vn_predictor.VnPredictor),
                 logger=cy_kit.singleton(LoggerService)):
        if isinstance(cyx.common.config.elastic_search,bool):
            return
        self.logger = logger
        self.config = cyx.common.config
        self.client = elasticsearch.Elasticsearch(
            hosts=cyx.common.config.elastic_search.server,
            timeout=30,
            sniff_timeout=30
        )
        self.prefix_index = cyx.common.config.elastic_search.prefix_index
        self.text_process_service = text_process_service
        self.file_content_extractor_service = file_content_extractor_service
        self.similarity_settings_cache = {}
        # "index.mapping.total_fields.limit": 2000
        self.__index_mapping_total_fields_limit = {}
        self.index_highlight_max_analyzed_offset = {}
        # self.vn = vn
        # self.vn_predictor = vn_predictor
        self.empty_privilege_value = 0

    def get_content_field_name(self):
        """
        File-Service use Elasticsearch document with below struct: \n
        {
            content:"..." //  text of any document will store here \n
            data_item: Dictionary // meta info when user upload or create blog

        }
        The method will return cy_es.DocumentFields("content")
        :return:
        """
        return self.config.elastic_search.field_content

    def delete_index(self, app_name):
        """
        Delete index
        :param app_name:
        :return:
        """
        self.client.indices.delete(index=self.get_index(app_name))

    def get_index(self, app_name):
        """
        Get index from app_name \n
        File-Service serves for multi  tenants. Each Tenant was represented by app_name \n
        File-Service will automatically create an Index according to  app_name and prefix \n
        prefix in YAML file config.yml at elastic_search.prefix_index (default value is 'lv-codx')
        Example: app_name is 'my-app' -> Elasticsearch Index Name is lv-codx_my-app \n
        Nhận chỉ mục từ app_name \n
        Dịch vụ tệp phục vụ cho nhiều người thuê. Mỗi Đối tượng thuê được đại diện bởi app_name \n
        Dịch vụ tệp sẽ tự động tạo Chỉ mục theo tên ứng dụng và tiền tố \n
        tiền tố trong tệp YAML config.yml tại elastic_search.prefix_index (giá trị mặc định là 'lv-codx')
        Ví dụ: app_name là 'my-app' -> Tên chỉ mục Elasticsearch là lv-codx_my-app \n
        Importance: many Elasticsearch settings will be applied in this method, such as : \n
            see link https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html \n
            max_result_window  see link  \n
            similarityedit see link https://www.elastic.co/guide/en/elasticsearch/reference/current/similarity.html


        :param app_name:
        :return:
        """
        if app_name == "admin":
            app_name = self.config.admin_db_name
        index_name = f"{self.prefix_index}_{app_name}"
        # if self.index_highlight_max_analyzed_offset.get(app_name) is None:
        #     self.client.indices.put_settings(
        #         index=index_name,
        #         body={
        #             "index.highlight.max_analyzed_offset": "10000"
        #         }
        #     )
        #     self.index_highlight_max_analyzed_offset[app_name] = 1
        #     self.client.indices.refresh(index_name)

        if self.similarity_settings_cache.get(app_name) is None:
            """
            Set ignore doc len when calculate search score 
            """
            try:
                cy_es.cy_es_x.similarity_settings(
                    client=self.client,
                    index=index_name,
                    field_name=self.get_content_field_name(),
                    algorithm_type="BM25", b_value=0, k1_value=10)
            except Exception as e:
                pass
            self.similarity_settings_cache[app_name] = True
        if self.__index_mapping_total_fields_limit.get(app_name) is None:
            """
            Defining too many fields in an index is a condition that can lead to a mapping explosion, which can 
            cause out of memory errors and difficult situations to recover from. This is quite common with dynamic 
            mappings. Every time a document contains new fields, those will end up in the index’s mappings
            ---------------------------------------------------
            Xác định quá nhiều trường trong một chỉ mục là một điều kiện có thể dẫn đến bùng nổ ánh xạ, có thể
            gây ra lỗi bộ nhớ và các tình huống khó phục hồi. Điều này khá phổ biến với động
            ánh xạ. Mỗi khi một tài liệu chứa các trường mới, chúng sẽ xuất hiện trong ánh xạ của chỉ mục
            """
            try:
                ret = self.client.indices.put_settings(index=index_name, body={
                    "index.mapping.total_fields.limit": 1000000

                })
                self.__index_mapping_total_fields_limit[app_name] = ret
            except Exception as e:
                """
                """
                self.__index_mapping_total_fields_limit[app_name] = e
        return index_name

    def delete_doc(self, app_name, id: str):
        """
        Delete Elasticsearch by id in application
        :param app_name:
        :param id:
        :return:
        """
        return cy_es.delete_doc(
            client=self.client,
            index=self.get_index(app_name),
            id=id
        )

    def mark_delete(self, app_name, id, mark_delete_value):
        """
        Some documents in Elasticsearch not show in any search. So, mark those documents is deleted \n
        Một số tài liệu trong Elaticsearch không hiển thị trong bất kỳ tìm kiếm nào. Vì vậy, hãy đánh dấu những tài liệu đó đã bị xóa
        :param app_name:
        :param id:
        :param mark_delete_value:
        :return:
        """
        ret = cy_es.update_doc_by_id(
            client=self.client,
            id=id,
            index=self.get_index(app_name),
            data=(
                cy_es.buiders.mark_delete << mark_delete_value,
            )
        )
        return ret

    def full_text_search(self,
                         app_name,
                         content,
                         page_size: typing.Optional[int],
                         page_index: typing.Optional[int],
                         highlight: typing.Optional[bool],
                         privileges: typing.Optional[dict],
                         sort: typing.List[str] = ["data_item.RegisterOn:desc"],
                         logic_filter=None):
        """
        There are many ways to search in Elasticsearch \n
        Search only content: \n
            full_text_search(app_name,content="my content search") \n
        or use logic_filter for searhing: \n
            full_text_search(app_name,content=None,logic_filter={
                    "$$search":{
                        "$fields":["conent"],
                        "$value":"my content search"
                    }
                }
            )


        :param app_name:
        :param content:
        :param page_size:
        :param page_index:
        :param highlight:
        :param privileges:
        :param sort:
        :param logic_filter:
        :return:
        """
        content = content or ""
        original_content = content

        if isinstance(privileges, dict):
            privileges = cy_es.text_lower(privileges)
        # content = self.vn_predictor.get_text(content)
        # content = original_content + " " + content
        # content_boots = self.vn.parse_word_segment(content=content, boot=[3])

        search_expr = (cy_es.buiders.mark_delete == False) | (cy_es.buiders.mark_delete == None)
        if privileges is not None and privileges != {}:
            search_expr = search_expr & cy_es.create_filter_from_dict(
                filter=
                cy_es.nested(
                    field_name="privileges",
                    filter=privileges
                ),
                suggest_handler=self.vn_predictor.get_text
            )
        # if content is not None and content != "" and content.lstrip().rstrip().strip() != "":
        #     content_search_match_phrase = cy_es.match_phrase(
        #         field=getattr(cy_es.buiders, "content"),
        #         content=content,
        #         boost=0.01,
        #         # slop=1,
        #         # analyzer="stop"
        #
        #     )
        #
        #     qr = cy_es.query_string(
        #         fields=[getattr(cy_es.buiders, f"{self.get_content_field_name()}_seg")],
        #         query=content_boots
        #         # slop=1
        #
        #     )
        #
        #     search_expr = search_expr & (content_search_match_phrase | qr)
        # search_expr.set_minimum_should_match(1)
        skip = page_index
        highlight_expr = None
        if highlight:
            """
            "highlight": {
    "require_field_match": "false",
    "fields": {
      "title": {},
      "email": {}
    }
  }
            """
            highlight_expr = [
                getattr(cy_es.buiders, f"content"),
                getattr(cy_es.buiders, f"{self.get_content_field_name()}_seg")
            ]
        if logic_filter is not None and isinstance(logic_filter, dict):
            _logic_filter = cy_es.create_filter_from_dict(
                logic_filter
            )
            if _logic_filter:
                search_expr = search_expr & _logic_filter
        highlight_expr = highlight_expr or []
        highlight_expr += search_expr.get_highlight_fields()
        print(f"------------{skip}--{page_size}-------------------------")
        t = datetime.datetime.now()
        from cy_es.cy_es_manager import FIELD_RAW_TEXT
        try:
            ret = cy_es.search(
                client=self.client,
                limit=page_size,
                excludes=[
                    cy_es.buiders.content,
                    getattr(cy_es.buiders, FIELD_RAW_TEXT),

                    cy_es.buiders.vn_on_accent_content],
                index=self.get_index(app_name),
                highlight=None,
                filter=search_expr,
                skip=skip,
                sort=sort

            )
            n = (datetime.datetime.now() - t).total_seconds()
            print(f"Elastic Search time = {n} second")
            return ret
        except elasticsearch.exceptions.RequestError as e:
            self.logger.error(e, more_info=search_expr)

            if hasattr(e, "info") and isinstance(e.info, dict) \
                    and e.info.get('error') \
                    and isinstance(e.info.get('error'), dict) \
                    and isinstance(e.info.get('error').get('root_cause'), list):

                if e.info['error']['root_cause'][0]['type'] == "illegal_argument_exception":
                    if "index.highlight.max_analyzed_offset] " in e.info['error']['root_cause'][0]['reason']:
                        max_value = e.info['error']['root_cause'][0]['reason'].split('The length [')[1].split(']')[0]
                        if app_name == "admin":
                            app_name = self.config.admin_db_name
                        index_name = f"{self.prefix_index}_{app_name}"
                        self.client.indices.put_settings(
                            index=index_name,
                            body={
                                "index.highlight.max_analyzed_offset": str((int(max_value) * 2))
                            }
                        )
                        self.client.indices.refresh(index_name)
                        ret = cy_es.search(
                            client=self.client,
                            limit=page_size,
                            excludes=[
                                cy_es.buiders.content,
                                cy_es.buiders.vn_on_accent_content],
                            index=self.get_index(app_name),
                            highlight=highlight_expr,
                            filter=search_expr,
                            skip=skip,
                            sort=sort

                        )
                        n = (datetime.datetime.now() - t).total_seconds()
                        print(f"Elastic Search time = {n} second")
                        return ret

            print(e)

    async def full_text_search_async(self,
                                     app_name,
                                     content,
                                     page_size: typing.Optional[int],
                                     page_index: typing.Optional[int],
                                     highlight: typing.Optional[bool],
                                     privileges: typing.Optional[dict],
                                     sort: typing.List[str] = ["data_item.RegisterOn:desc"],
                                     logic_filter=None):
        return self.full_text_search(
            app_name,
            content,
            page_size,
            page_index,
            highlight,
            privileges,
            sort,
            logic_filter
        )

    def get_doc(self, app_name: str, id: str, doc_type: str = "_doc"):
        """
        get document by id

        :param app_name:
        :param id:
        :param doc_type:
        :return:
        """
        return cy_es.get_doc(client=self.client, id=id, doc_type=doc_type, index=self.get_index(app_name))

    def get_source(self, app_name: str, id: str):
        return cy_es.cy_es_objective.get_source(
            client=self.client,
            id=id,
            index=self.get_index(app_name)
        )

    async def get_doc_async(self, app_name: str, id: str, doc_type: str = "_doc"):
        return await cy_es.get_doc_async(client=self.client, id=id, doc_type=doc_type, index=self.get_index(app_name))

    def copy(self, app_name: str, from_id: str, to_id: str, attach_data, run_in_thread: bool = True):
        """
        Copy ES doc into new
        :param app_name:
        :param from_id:
        :param to_id:
        :param attach_data:
        :param run_in_thread:
        :return:
        """

        @cy_kit.thread_makeup()
        def copy_elastics_search(app_name: str, from_id: str, to_id: str, attach_data):
            es_doc = self.get_doc(id=from_id, app_name=app_name)
            if es_doc:
                es_doc.source.upload_id = to_id
                es_doc.source.data_item = attach_data
                es_doc.source["mark_delete"] = False
                ret = self.create_doc(app_name=app_name, id=to_id, body=es_doc.source)

        if run_in_thread:
            copy_elastics_search(app_name, from_id, to_id, attach_data).start()
        else:
            copy_elastics_search(app_name, from_id, to_id, attach_data).start().join()

    def create_doc(self, app_name, id: str, body):
        return cy_es.create_doc(
            client=self.client,
            index=self.get_index(app_name),
            id=id,
            body=body
        )

    def make_index_content(self, app_name: str,
                           upload_id: str,
                           data_item: dict|None,
                           privileges: dict,
                           path_to_file_content: str = None,
                           content: str = None,
                           meta_info=None,
                           mark_delete=False,
                           meta_data=None):
        """
        Make index content: \n
        File-Service use Elasticsearch Document with struct below:
            {
                _id: upload_id // use upload_id
                content: // any content of document here
                data_item: // data_item get from Mongodb File-Service
                meta_info: // any information come from another application in which use File-Service \n
                            //bất kỳ thông tin nào đến từ một ứng dụng khác sử dụng Dịch vụ tệp

                meta_data: // The  file information which was generated by OS or software create file \n
                           // Thông tin tệp được tạo bởi hệ điều hành hoặc phần mềm tạo tệp
            }
        :param app_name: representative app_name of tenant
        :param upload_id: id of Upload file
        :param data_item: data was created when end-user upload file or create blog
        :param privileges: privileges tags use to restrict un-allow access document from en-user \n thẻ đặc quyền sử dụng để hạn chế không cho phép truy cập tài liệu từ người dùng

        :param path_to_file_content: full path to file content if content of ES document get from file, please set path_to_file_content
        :param content: if content of ES document does not get from file, please set content here
        :param meta_info: any information come from another application in which use File-Service
        :param mark_delete:
        :param meta_data: The  file information which was generated by OS or software create file
        :return:
        """
        if data_item is None:
            return
        file_name = None
        if path_to_file_content is not None:
            content, meta_info = self.file_content_extractor_service.get_text(path_to_file_content)
            file_name = pathlib.Path(path_to_file_content).name
        elif content is None:
            content, meta_info = None, None
            file_name = None
        index_name = self.get_index(app_name)

        vn_non_accent_content = self.text_process_service.vn_clear_accent_mark(content)
        body_dict = dict(
            app_name=app_name,
            upload_id=upload_id,
            file_name=file_name,
            mark_delete=mark_delete,
            content=content,
            meta_info = meta_info or data_item.get('meta_data'),
            data_item = data_item or {},
            privileges=privileges,
            meta_data=meta_data
        )

        # body_dict[f"{self.get_content_field_name()}_lower"] = self.vn.parse_word_segment(content=content.lower())
        cy_es.create_doc(
            client=self.client,
            index=index_name,
            id=upload_id,
            body=body_dict
        )

        del content
        del meta_info
        del vn_non_accent_content

    def create_or_update_privileges(
            self,
            app_name, upload_id,
            data_item: typing.Union[dict, cy_docs.DocumentObject, None],
            privileges,
            meta_info: dict = None,
            force_replace: bool = False
    ):
        """
        Create or update privileges tag
        if set upload_id the method will find and update else the method will automatically create new document \n
        nếu được đặt upload_id, phương thức sẽ tìm và cập nhật, nếu không, phương thức sẽ tự động tạo tài liệu mới
        :param app_name:
        :param upload_id:
        :param data_item: will skip if update
        :param privileges:
        :param meta_info: will replace meta_info of ES document
        :return:
        """
        is_exist = self.is_exist(app_name, id=upload_id)

        if is_exist:
            if data_item:
                return cy_es.update_doc_by_id(
                    client=self.client,
                    index=self.get_index(app_name),
                    id=upload_id,
                    data=(
                        cy_es.buiders.privileges << privileges,
                        cy_es.buiders.meta_info << meta_info
                    ),
                    force_replace=force_replace
                )
            else:
                return cy_es.update_doc_by_id(
                    client=self.client,
                    index=self.get_index(app_name),
                    id=upload_id,
                    data=(
                        cy_es.buiders.privileges << privileges,
                        cy_es.buiders.meta_info << meta_info
                    ),
                    force_replace=force_replace
                )
        else:
            if data_item:
                self.make_index_content(
                    app_name=app_name,
                    privileges=privileges,
                    upload_id=upload_id,

                    data_item = data_item,
                    meta_info=meta_info
                )
            else:
                self.make_index_content(
                    app_name=app_name,
                    privileges=privileges,
                    upload_id=upload_id,
                    data_item=None,
                    meta_info=meta_info
                )

    def is_exist(self, app_name: str, id: str) -> bool:
        return cy_es.is_exist(
            client=self.client,
            index=self.get_index(app_name),
            id=id
        )

    def update_content_value_only(self, app_name: str, id: str,
                                  content: str,
                                  content_lower: str,
                                  content_field="content"):
        """
        Update content of ES document \n
        File-Service use Elasticsearch Document with struct below:
            {
                _id: upload_id // use upload_id
                content: // any content of document here
                data_item: // data_item get from Mongodb File-Service
                meta_info: // any information come from another application in which use File-Service \n
                            //bất kỳ thông tin nào đến từ một ứng dụng khác sử dụng Dịch vụ tệp

                meta_data: // The  file information which was generated by OS or software create file \n
                           // Thông tin tệp được tạo bởi hệ điều hành hoặc phần mềm tạo tệp
            }
        The method just update content and create content_lower (content in lower-case) and content_seg (content in word_segmenter)
        See link https://github.com/Sudo-VP/Vietnamese-Word-Segmentation-Python
        :param app_name:
        :param id:
        :param content:
        :param content_lower:
        :param content_field:
        :return:
        """
        is_exist = self.is_exist(app_name, id=id)
        if is_exist:
            return cy_es.update_doc_by_id(
                client=self.client,
                index=self.get_index(app_name),
                id=id,
                data=(
                        getattr(cy_es.buiders, content_field) << content
                    # getattr(cy_es.buiders, f"{content_field}_lower") << content_lower,
                    # getattr(cy_es.buiders, f"{content_field}_seg") << content,

                )
            )

    def update_content(self, app_name: str,
                       id: str, content: str,
                       data_item=None,
                       meta_info: dict = None,
                       meta_data: dict = None,
                       replace_content=False,
                       update_meta=True):

        original_content = content or ""
        content = content or ""

        if data_item is None:
            return
        is_exist = self.is_exist(app_name, id=id)
        if isinstance(data_item, cy_docs.DocumentObject):
            json_data_item = data_item.to_json_convertable()
        elif isinstance(data_item, dict):
            json_data_item = cy_docs.to_json_convertable(data_item)
        if is_exist:
            es_doc = self.get_doc(
                app_name=app_name,
                id=id

            )
            # if not replace_content:
            #     old_content = self.vn_predictor.get_text(es_doc.source.content or "")
            #     content = content + "\n" + self.vn_predictor.get_text(content)
            #     content = content + "\n" + old_content
            #
            #     vn_non_accent_content = self.text_process_service.vn_clear_accent_mark(content)
            # else:
            #     if content and content != "":
            #         vn_non_accent_content = self.text_process_service.vn_clear_accent_mark(content)
            #         content = content + "\r\n" + self.vn_predictor.get_text(content)
            #     else:
            #         content = es_doc.source.content or ""
            #         vn_non_accent_content = self.text_process_service.vn_clear_accent_mark(content)
            #         content = content + "\r\n" + self.vn_predictor.get_text(content)
            _Privileges = None
            if hasattr(data_item, "Privileges"):
                _Privileges = data_item.Privileges
            elif isinstance(data_item, dict):
                _Privileges = data_item.get("Privileges")
            # seg_content = self.vn.parse_word_segment(
            #     content=content
            # )
            _Privileges = json_data_item.get("Privileges") or _Privileges
            if isinstance(_Privileges, cy_docs.DocumentObject):
                _Privileges = _Privileges.to_json_convertable()
            meta_info = (meta_info or es_doc.source.get('meta_info')) or json_data_item.get('meta_data')
            meta_data = meta_data or es_doc.source.get('meta_data')
            return cy_es.update_doc_by_id(
                client=self.client,
                index=self.get_index(app_name),
                id=id,
                data=(
                    cy_es.buiders.privileges << _Privileges,
                    getattr(cy_es.buiders, f"{self.get_content_field_name()}") << content,
                    # cy_es.buiders.vn_non_accent_content << vn_non_accent_content,
                    cy_es.buiders.content << content,
                    cy_es.buiders.data_item << json_data_item,
                    cy_es.buiders.meta_info << meta_info,
                    cy_es.buiders.meta_data << meta_data

                )
            )
        else:
            if not replace_content:
                content = original_content + "\n" + content
            _Privileges = None
            if hasattr(data_item, "Privileges"):
                _Privileges = data_item.Privileges
            elif isinstance(data_item, dict):
                _Privileges = data_item.get("Privileges")
            _mark_delete = False
            if hasattr(data_item, "mark_delete"):
                _mark_delete = data_item.mark_delete
            self.make_index_content(
                app_name=app_name,
                privileges=_Privileges,
                upload_id=id,
                # data_item=cy_es.convert_to_vn_predict_seg(
                #     json_data_item,
                #     handler=self.vn_predictor.get_text,
                #     segment_handler=self.vn.parse_word_segment,
                #     clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
                # ),
                data_item = data_item,
                content=content,
                meta_info=meta_info,
                meta_data=meta_data,
                mark_delete=_mark_delete,

            )

    def update_data_field(self, app_name, id, field_path, field_value):
        cy_es.update_data_fields(
            index=self.get_index(app_name),
            id=id,
            field_path=field_path,
            field_value=field_value,
            client=self.client

        )
        if cy_es.is_content_text(field_value):
            vn_predictor = self.vn_predictor.get_text(field_value)
            vn_seg = self.vn.parse_word_segment(vn_predictor)
            if vn_predictor != field_value:
                cy_es.update_data_fields(
                    index=self.get_index(app_name),
                    id=id,
                    field_path=f"{field_path}_vn_predict",
                    field_value=vn_predictor,
                    client=self.client

                )
            cy_es.update_data_fields(
                index=self.get_index(app_name),
                id=id,
                field_path=f"{field_path}_bm25_seg",
                field_value=vn_seg,
                client=self.client

            )

    def update_by_conditional(self, app_name, conditional, data):
        if isinstance(conditional, dict):
            conditional = cy_es.create_filter_from_dict(conditional)
        return cy_es.update_by_conditional(
            client=self.client,
            data_update=cy_es.convert_to_vn_predict_seg(
                data,
                handler=self.vn_predictor.get_text,
                segment_handler=self.vn.parse_word_segment,
                clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
            ),
            index=self.get_index(app_name),
            conditional=conditional
        )

    def delete_by_conditional(self, app_name, conditional):
        if isinstance(conditional, dict):
            conditional = cy_es.create_filter_from_dict(conditional)
        return cy_es.delete_by_conditional(
            client=self.client,
            index=self.get_index(app_name),
            conditional=conditional
        )

    def fix_privilges_list_error(self, privileges):
        """
        Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
        :param privileges:
        :return:
        """
        if isinstance(privileges, list):
            ret = []
            for x in privileges:
                if x.Values == "":
                    x.Values = self.empty_privilege_value
                ret += [x]
            return ret
        return privileges

    def fix_privilges_contains_error(self, data_privileges):
        """
                    Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
                    :param data_privileges:
                    :return:
                    """
        if isinstance(data_privileges, dict):
            for k, v in data_privileges.items():
                if k == "$contains" and v == ['']:
                    data_privileges[k] = [self.empty_privilege_value]
                else:
                    data_privileges[k] = self.fix_privilges_contains_error(v)
        elif isinstance(data_privileges, list):
            return [self.fix_privilges_contains_error(x) for x in data_privileges]
        else:
            return data_privileges
        return data_privileges

    def update_data_fields(self, app_name: str, id: str, data: dict):
        assert isinstance(data, dict), "data args must be dic"
        for k, v in data.items():
            self.update_data_field(
                app_name=app_name,
                id=id,
                field_path=k,
                field_value=v
            )

    def replace_content(self, app_name, id, field_path: str, field_value: str, timeout="60s"):
        cy_es.replace_content(
            index=self.get_index(app_name),
            id=id,
            field_path=field_path,
            field_value=field_value,
            client=self.client,
            timeout=timeout

        )
        print(app_name)
        pass
