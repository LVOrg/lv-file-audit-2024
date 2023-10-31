# import fastapi
#
# import cy_es
# import cy_xdoc.services.search_engine
# import cy_kit
# import cy_web
# import cy_xdoc.auths
# from typing import Optional
# @cy_web.hanlder("post","{app_name}/search")
# async def file_search(app_name: str, content: Optional[str],
#                       page_size: Optional[int],
#                       page_index: Optional[int],
#                       highlight: Optional[bool],
#                       privileges: Optional[dict],
#                       logic_filter: Optional[dict],
#                       filter: Optional[str],
#                       token = fastapi.Depends(cy_xdoc.auths.Authenticate)):
#     """
#     <br/>
#     <p>
#     <b>For a certain pair of Application and  Access Token </b><br/>
#     This API allow thou search content in full content of any document.<br>
#     <code>\n
#         {
#             content:<any text for searching>,
#             page_size: <limit search result>,
#             page_index: <page index of result, start value is 0>,
#             highlight: <Highlight match content if set true>,
#             privileges: <JSON filter>,
#             filter: 'day(data_item.RegisterOn)=22 and (data_item.Filename, content) search "my text"'
#
#         }
#     </code>
#     <p >
#         <b style='color:red !important'> Highlight maybe crash Elasticsearch or ake very long time </b>
#     <p>
#     <h1>
#      How to make privileges filter json expression?
#     </h1>
#     <div>
#         Privileges filter json expression has some bellow key words (they are nested together):
#         <ol>
#             <li><b>$and</b>: and logical follow by list of other filters.</li>
#             <li><b>$or</b>: or logical follow by list of other filters.</li>
#             <li><b>$not</b>: negative a filter expression.</li>
#             <li><b>$contains</b>: check a privileges has contains a list of values.</li>
#         </ol>
#     </div>
#     <code>\n
#         docs = [
#                  {
#                     id:1,
#                     users:['admin','root'],
#                     position: ['staff','deputy']
#                  } ,
#                  {
#                     id:2,
#                     users :['root','admin','user1'],
#                     position: ['director','deputy']
#                  }
#                 ]
#         //Example filter all document share to user root and admin only
#         filter ={
#                     users:['root','admin']
#                 }
#         thou will get docs=[{id:1}]
#
#         //filter all document has share root and admin
#         filter ={
#                     users:{
#                         $contains:['root','admin']
#                     }
#
#                 }
#         //filter all document share to director position but deputy
#         filter = {
#                     $and:[
#                         {
#                             position:{
#                                 $contains:['director']
#                             },
#                             {
#                                 $not: {
#                                     position:{
#                                         $contains:['deputy']
#                                     }
#                                 }
#                             }
#                         }
#                     ]
#                 }
#
#     </code>
#
#     </p>
#     :param privileges: <p> Filter by privileges<br/> The privileges tags is a pair key and values </p>
#     :param request:
#     :param app_name:
#     :param content:
#     :param page_size:
#     :param page_index:
#     :param token:
#     :return:
#     """
#     from cy_xdoc.controllers import files_content_search_utils
#
#     # from cy_xdoc.controllers.apps import check_app
#     # check_app(app_name)
#     if highlight is None:
#         highlight=False
#     search_services: cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(cy_xdoc.services.search_engine.SearchEngine)
#     # search_result = search_content_of_file(app_name, content, page_size, page_index)
#     json_filter = None
#
#     if filter is not None and filter.__len__()>0:
#         if logic_filter:
#             try:
#                 json_filter = cy_es.natural_logic_parse(filter)
#                 logic_filter = {
#                     "$and":[logic_filter,json_filter]
#                 }
#             except Exception as e:
#                 return fastapi.Response(
#                     content= f"{filter} is error syntax",
#                     status_code= 501
#                 )
#         else:
#             try:
#                 json_filter = cy_es.natural_logic_parse(filter)
#                 logic_filter = json_filter
#
#             except Exception as e:
#                 return fastapi.Response(
#                     content= f"{filter} is error syntax",
#                     status_code= 501
#                 )
#     search_result= search_services.full_text_search(
#         app_name=app_name,
#         content =content,
#         page_size=page_size,
#         page_index=page_index,
#         highlight=highlight,
#         privileges= privileges,
#         logic_filter=logic_filter
#     )
#
#
#
#
#     ret_items = files_content_search_utils.pack_list(
#         url= cy_web.get_host_url() + "/api",
#         app_name= app_name,
#         items = search_result.items
#     )
#
#     return dict(
#         total_items=search_result.hits.total,
#         max_score=search_result.hits.max_score,
#         items=ret_items,
#         text_search=content,
#         json_filter = json_filter
#     )
