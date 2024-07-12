import pathlib
import typing
import cy_docs
import cy_es

import elasticsearch
from cyx.common import config


class ElasticSearchUtilService:
    def __init__(self):

        self.client = elasticsearch.Elasticsearch(
            hosts=config.elastic_search.server,
            timeout=30,
            sniff_timeout=30
        )
        self.prefix_index = config.elastic_search.prefix_index
        self.similarity_settings_cache = {}
        # "index.mapping.total_fields.limit": 2000
        self.__index_mapping_total_fields_limit = {}
        self.index_highlight_max_analyzed_offset = {}
        # self.vn = vn
        # self.vn_predictor = vn_predictor
        self.empty_privilege_value = 0
        self.admin_db_name = config.admin_db_name
        self.__index_mapping_total_fields_limit = dict()

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
            app_name = self.admin_db_name
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

    def is_exist(self, app_name: str, id: str) -> bool:
        return cy_es.is_exist(
            client=self.client,
            index=self.get_index(app_name),
            id=id
        )
    def make_index_content(self, app_name: str,
                           upload_id: str,
                           data_item: dict,
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
        file_name = pathlib.Path(path_to_file_content).name if path_to_file_content is not None else None
        index_name = self.get_index(app_name)
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
                    # data_item=cy_es.convert_to_vn_predict_seg(
                    #     data_item,
                    #     segment_handler=self.vn.parse_word_segment,
                    #     handler=self.vn_predictor.get_text,
                    #     clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
                    # ),
                    data_item=data_item,
                    meta_info=meta_info
                )
            else:
                self.make_index_content(
                    app_name=app_name,
                    privileges=privileges,
                    upload_id=upload_id,
                    data_item=None,
                    meta_info=meta_info,
                    force_replace=force_replace
                )

    def create_privileges(self, privileges_type_from_client: dict) -> typing.Tuple[typing.Dict, typing.Dict]:
        """
        Chuyen doi danh sach cac dac quyen do nguoi dung tao sang dang luu tru trong mongodb va elastic search
        Dong thoi ham nay cung update lai danh sach tham khao danh cho giao dien
        Trong Mongodb la 2 ban Privileges, PrivilegesValues
        :param app_name:
        :param privileges_type_from_client:
        :return: (privileges_server,privileges_client)
        """

        privileges_server = {}
        privileges_client = []
        if privileges_type_from_client:

            check_types = dict()
            for x in privileges_type_from_client:
                if check_types.get(x.Type.lower().strip()) is None:
                    privileges_server[x.Type.lower()] = [v.strip() for v in x.Values.lower().split(',')]
                    privileges_client += [{
                        x.Type: x.Values
                    }]
                check_types[x.Type.lower().strip()] = x
        return privileges_server, privileges_client
