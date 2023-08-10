import typing

import cy_kit
import cyx.common
import elasticsearch
import cy_es


class ClientConfig:
    client: elasticsearch.Elasticsearch
    key: str


class ClientFactoryService:
    def __init__(self):
        self.config = cyx.common.config
        self.__clients__ = {}

    def get_client(self, server: typing.Optional[typing.Union[typing.List[str], str]] = None) -> ClientConfig:
        if server:
            key = server
            if isinstance(server, list):
                key = ",".join(server)
            if self.__clients__.get(server):
                return self.__clients__[server]
            else:
                ret = ClientConfig()
                ret.client = elasticsearch.Elasticsearch(
                    server
                )
                ret.key = key
                self.__clients__[key] = ret
        else:
            key = ",".join(cyx.common.config.elastic_search.server)
            if not self.__clients__.get(key):
                ret = ClientConfig()
                ret.client = elasticsearch.Elasticsearch(
                    cyx.common.config.elastic_search.server
                )
                ret.key = key
                self.__clients__[key] = ret
            return self.__clients__[key]


class ClientContext:
    def __init__(self, client: elasticsearch.Elasticsearch, key: str, index: str):
        self.key = key
        self.client = client
        self.index = index
        self.__settings__ = None

    def get_settings(self)->dict:
        if self.__settings__ is None:
            ret = self.client.indices.get_settings(
                index=self.index
            )
            ret =ret[list(ret.keys())[0]]
            ret = ret[list(ret.keys())[0]]
            self.__settings__ = ret[list(ret.keys())[0]]
        return self.__settings__
    def get_similarity(self,name:str='similarity')->dict:
        settings = self.get_settings()
        if settings.get(name):
            return settings.get(name)
        else:
            return None
    def get_total_fields_limit(self)->typing.Optional[int]:
        settings = self.get_settings()
        if settings.get('mapping') and settings.get('mapping').get('total_fields') and settings.get('mapping').get('total_fields').get('limit'):
            return int(self.get_settings().get('mapping').get('total_fields').get('limit'))
        else:
            return None

    def set_total_fields_limit(self, size:typing.Union[int,float]):
        ret = self.client.indices.put_settings(index=self.index, body={
            "index.mapping.total_fields.limit":  int(size)

        })
        return ret

    def add_similarity(self,
                       name:str,
                       algorithm_type: str= "BM25",
                       b_k:typing.Tuple[float,float] = (0,10)):
        self.client.indices.close(index=self.index)
        settings = {
            "index": {
                "similarity": {
                    name: {
                        "type": algorithm_type,
                        "b": b_k[0],  # b gần về 0 sẽ bỏ qua độ dài của câu
                        "k1": b_k[1]
                    }
                }
            }
        }
        self.client.indices.put_settings(index=self.index, body=settings)
        self.client.indices.open(index=self.index)

    def add_similarity_fields(self,name:str, fields:typing.List[str] ,algorithm_type: str= "BM25", b_k:typing.Tuple[float,float] = (0,10)):
        similarity = self.get_similarity(name)
        if similarity is None:
            self.add_similarity(name,algorithm_type,b_k)
        self.client.indices.close(index=self.index)
        properties = {
                x: {
                    "type" : "text",
                    "similarity": name,
                    "fielddata": True
                }
             for x in fields
        }
        self.client.indices.put_mapping(
            index=self.index,
            body=
            {
                "properties": properties
            }
        )
        self.client.indices.open(index=self.index)

    def create_new_field_from_exist_field(self, source:str, dest: str,doc_type="_doc"):
        try:
            """
            doc['{self.__name__}.keyword'].value
            """
            self.client.search(index=self.index, doc_type=doc_type, body={
                '_source': True,
                'script_fields': {
                    dest: {
                        'script': {
                            'source': 'if (doc["'+source+'"].size()>0) { return doc["'+source+'"].value;} else {return "";}'
                        }
                    }
                }
            })
        except elasticsearch.exceptions.RequestError  as e:
            for k,v in e.info.items():
                print(k)
                print(v)
                print("-------------------------------")
            raise e
        except Exception as e:
            print(e)

    def select(self, filter:typing.Union[dict,cy_es.DocumentFields], fields:typing.List[str], page_index:int=0,page_size:int=100):
        query = filter
        if isinstance(filter,cy_es.DocumentFields):
            query = filter.__es_expr__
        ret = self.client.search(
            index = self.index,
            body =
            {
                "query": query,
                "fields": fields,
                "_source": False,
                "from": page_size*page_index,
                "size": page_size,

            }, doc_type = "_doc"
        )

        return ret["hits"]["hits"]


class ElasticSearchUtilsService:
    def __init__(self, client_factory_service=cy_kit.singleton(ClientFactoryService)):
        self.config = cyx.common.config
        self.client = client_factory_service.get_client()
        self.prefix_index = cyx.common.config.elastic_search.prefix_index
        self.__client_context__ = {}
        self.similarity_settings_cache = {}

    def get_context(self, app_name: str) -> ClientContext:
        app_name = app_name.lower()
        if not isinstance(self.__client_context__.get(app_name),ClientContext):
            index = self.__get_index__(app_name)
            self.__client_context__[app_name] = ClientContext(self.client.client, self.client.key, index=index)
        return self.__client_context__.get(app_name)

    def __get_index__(self, app_name):
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
        # if self.similarity_settings_cache.get(app_name) is None:
        #     """
        #     Set ignore doc len when calculate search score
        #     """
        #     cy_es.cy_es_x.similarity_settings(
        #         client=self.client,
        #         index=index_name,
        #         field_name=self.get_content_field_name(),
        #         algorithm_type="BM25", b_value=0, k1_value=10)
        #     self.similarity_settings_cache[app_name] = True
        # if self.__index_mapping_total_fields_limit.get(app_name) is None:
        #     """
        #     Defining too many fields in an index is a condition that can lead to a mapping explosion, which can
        #     cause out of memory errors and difficult situations to recover from. This is quite common with dynamic
        #     mappings. Every time a document contains new fields, those will end up in the index’s mappings
        #     ---------------------------------------------------
        #     Xác định quá nhiều trường trong một chỉ mục là một điều kiện có thể dẫn đến bùng nổ ánh xạ, có thể
        #     gây ra lỗi bộ nhớ và các tình huống khó phục hồi. Điều này khá phổ biến với động
        #     ánh xạ. Mỗi khi một tài liệu chứa các trường mới, chúng sẽ xuất hiện trong ánh xạ của chỉ mục
        #     """
        #     try:
        #         ret = self.client.indices.put_settings(index=index_name, body={
        #             "index.mapping.total_fields.limit": 1000000
        #
        #         })
        #         self.__index_mapping_total_fields_limit[app_name] = ret
        #     except Exception as e:
        #         """
        #         """
        #         self.__index_mapping_total_fields_limit[app_name] = e
        return index_name
