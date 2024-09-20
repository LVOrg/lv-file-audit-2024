import datetime
import typing
import fastapi
from cy_controllers.models.apps import(
        AppInfo,
        AppInfoRegister,
        AppInfoRegisterResult,
        ErrorResult, AppInfoRegisterModel
    )
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    Body
)
from cy_xdoc.auths import Authenticate
import cy_es
import cy_web
router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
import pymongo
@controller.resource()
class SearchController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def pack_list(self,url: str, app_name: str, items):
        ret_items = []

        for x in items:
            upload_doc_item = x._source.data_item
            if upload_doc_item:
                # upload_doc_item.UploadId = upload_doc_item._id
                upload_doc_item.Highlight = x.highlight

                upload_doc_item.AppName = app_name
                if hasattr(upload_doc_item, "FullFileName") and upload_doc_item.FullFileName is not None:
                    upload_doc_item.RelUrlOfServerPath = f"/{app_name}/file/{upload_doc_item.FullFileName}"
                    upload_doc_item.UrlOfServerPath = f"{url}/{app_name}/file/{upload_doc_item.FullFileName}"
                if hasattr(upload_doc_item, "FileName") and upload_doc_item.FileName is not None:
                    upload_doc_item.ThumbUrl = url + f"/{app_name}/thumb/{upload_doc_item['_id']}/{upload_doc_item.FileName}.png"

                upload_doc_item.privileges = x._source.get('privileges')
                upload_doc_item.meta_data =  x._source.get('meta_info')
                upload_doc_item.__score__ = x._score
                ret_items += [upload_doc_item]
        return ret_items

    async def pack_list_async(self,url: str, app_name: str, items):
        return self.pack_list(url, app_name, items)
    @controller.router.post("/api/{app_name}/content/update_by_conditional")
    def file_content_update_by_conditional(
            self,
            app_name: str,
            conditional:typing.Optional[dict]=Body(...),
            conditional_text: typing.Optional[str]=Body(...),
            data_update: typing.Optional[dict]=Body(...)):
        """
        Update data to search engine with conditional<br/>
        Cập nhật dữ liệu lên công cụ tìm kiếm có điều kiện
        :param app_name:
        :param data_update:
        :param conditional_text:
        :return:
        """
        if conditional_text:
            conditional = cy_es.natural_logic_parse(conditional_text)
        ret = self.search_engine.update_by_conditional(
            app_name=app_name,
            conditional=conditional,
            data=data_update
        )
        return ret

    @controller.router.post("/api/{app_name}/search",tags=["SEARCH"])
    async def file_search(self,
                          app_name: str,
                          content: typing.Optional[str]= fastapi.Body(default=None) ,
                          page_size:  typing.Optional[int] = fastapi.Body(default=20),
                          page_index:  typing.Optional[int] = fastapi.Body(default=0),
                          highlight:  typing.Optional[bool] = fastapi.Body(default=False),
                          privileges:  typing.Optional[dict] = fastapi.Body(default=None),
                          logic_filter:  typing.Optional[dict] = fastapi.Body(default=None),
                          filter:  typing.Optional[str] = fastapi.Body(default=None)):
        """
        <br/>
        <p>
        <b>For a certain pair of Application and  Access Token </b><br/>
        This API allow thou search content in full content of any document.<br>
        <code>\n
            {
                content:<any text for searching>,
                page_size: <limit search result>,
                page_index: <page index of result, start value is 0>,
                highlight: <Highlight match content if set true>,
                privileges: <JSON filter>,
                filter: 'day(data_item.RegisterOn)=22 and (data_item.Filename, content) search "my text"'

            }
        </code>
        <p >
            <b style='color:red !important'> Highlight maybe crash Elasticsearch or ake very long time </b>
        <p>
        <h1>
         How to make privileges filter json expression?
        </h1>
        <div>
            Privileges filter json expression has some bellow key words (they are nested together):
            <ol>
                <li><b>$and</b>: and logical follow by list of other filters.</li>
                <li><b>$or</b>: or logical follow by list of other filters.</li>
                <li><b>$not</b>: negative a filter expression.</li>
                <li><b>$contains</b>: check a privileges has contains a list of values.</li>
            </ol>
        </div>
        <code>\n
            docs = [
                     {
                        id:1,
                        users:['admin','root'],
                        position: ['staff','deputy']
                     } ,
                     {
                        id:2,
                        users :['root','admin','user1'],
                        position: ['director','deputy']
                     }
                    ]
            //Example filter all document share to user root and admin only
            filter ={
                        users:['root','admin']
                    }
            thou will get docs=[{id:1}]

            //filter all document has share root and admin
            filter ={
                        users:{
                            $contains:['root','admin']
                        }

                    }
            //filter all document share to director position but deputy
            filter = {
                        $and:[
                            {
                                position:{
                                    $contains:['director']
                                },
                                {
                                    $not: {
                                        position:{
                                            $contains:['deputy']
                                        }
                                    }
                                }
                            }
                        ]
                    }

        </code>

        </p>
        :param privileges: <p> Filter by privileges<br/> The privileges tags is a pair key and values </p>
        :param request:
        :param app_name:
        :param content:
        :param page_size:
        :param page_index:
        :param token:
        :return:
        """





        if highlight is None:
            highlight = False
        # search_services: cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(
        #     cy_xdoc.services.search_engine.SearchEngine)
        # search_result = search_content_of_file(app_name, content, page_size, page_index)
        json_filter = None

        if filter is not None and filter.__len__() > 0:
            if logic_filter:
                try:
                    json_filter = cy_es.natural_logic_parse(filter)
                    logic_filter = {
                        "$and": [logic_filter, json_filter]
                    }
                except Exception as e:
                    return Response(
                        content=f"{filter} is error syntax",
                        status_code=501
                    )
            else:
                try:
                    json_filter = cy_es.natural_logic_parse(filter)
                    logic_filter = json_filter

                except Exception as e:
                    return Response(
                        content=f"{filter} is error syntax",
                        status_code=501
                    )
        search_result =  self.search_engine.full_text_search(
            app_name=app_name,
            content=content,
            page_size=page_size,
            page_index=page_index,
            highlight=highlight,
            privileges=privileges,
            logic_filter=logic_filter
        )

        ret_items = self.pack_list(
            url=cy_web.get_host_url(self.request) + "/api",
            app_name=app_name,
            items=search_result.items
        )

        return dict(
            total_items=search_result.hits.total,
            max_score=search_result.hits.max_score,
            items=ret_items,
            text_search=content,
            json_filter=json_filter
        )

    @controller.router.post("/api/{app_name}/meta_info/get",tags=["SEARCH"])
    async def read_meta_info_async(self,app_name:str,UploadId:str=Body(embed=True)):
        es= self.search_engine.client
        es_index = self.search_engine.get_index(app_name)
        result = es.get(index=es_index, id=UploadId, _source=["meta_info"],doc_type="_doc")
        if not result:
            raise Exception(f"{UploadId} was not found in {app_name}")
        return result.get("_source",{}).get("meta_info")

    @controller.router.post("/api/{app_name}/meta_info/save", tags=["SEARCH"])
    async def read_meta_info_async(self, app_name: str, UploadId: str = Body(embed=True),meta:dict=Body(embed=True)):
        es = self.search_engine.client
        es_index = self.search_engine.get_index(app_name)
        doc_id = UploadId
        update_data = {
            "doc": {
                "meta_info": meta
            }
        }
        ret = es.update(index=es_index, id=doc_id, body=update_data,doc_type="_doc")
        return ret.get('result')

