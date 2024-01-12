import pathlib
import sys
import time

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append("/app")

import cy_kit
import elasticsearch
from cyx.loggers import LoggerService
logger = cy_kit.singleton(LoggerService)
from cy_xdoc.services.files import FileServices
files = cy_kit.singleton(FileServices)

from cy_es import cy_es_manager
from cy_xdoc.services.search_engine import SearchEngine
se = cy_kit.singleton(SearchEngine)
es: elasticsearch.Elasticsearch =se.client

FX=getattr(cy_es_manager.filters,f"{cy_es_manager.FIELD_RAW_TEXT}_FIX")
Filter_byFile = cy_es_manager.filters.data_item.SizeInBytes>0
skip_index=[]
running=True
while running:
    list_of_index = cy_es_manager.get_all_indexes(
        client=es,
        prefix="lv-codx_"
    )
    runnning_index= list(set(list_of_index).difference(set(skip_index)))
    for index_name in runnning_index:
        ret,total = cy_es_manager.get_docs(
            client=es,
            index=index_name,
            fields=[
                "app_name"
            ],
            filter = Filter_byFile & ((FX==False) | (FX==None))
        )
        if total==0:
            skip_index+=[index_name]
            break
        for x in ret:
            try:
                if x.get(cy_es_manager.FIELD_RAW_TEXT) is not  None:
                    del  x[cy_es_manager.FIELD_RAW_TEXT]
                print(f"{index_name}={x['_id']}")

                doc = cy_es_manager.get_doc(
                    client=es,
                    index=index_name,
                    id= x["_id"] # x["_id"]
                )
                doc= cy_es_manager.clean_up(doc)
                print(len(doc.get("content") or ""))
                result,u_data = cy_es_manager.update_doc_by_id(
                    client=es,
                    index = index_name,
                    id = x["_id"],
                    data = doc,
                    skip_update_mapping=False
                )

                print(f"{index_name}={x['_id']} complete")
                app_name=index_name[len("lv-codx_"):]
                from cy_xdoc.models.files import DocUploadRegister
                from cyx.common.base import DbCollection
                doc: DbCollection[DocUploadRegister] = files.db_connect.db(app_name).doc(DocUploadRegister)
                doc.context.update(
                    doc.fields.id==x['_id'],
                    doc.fields.Search_vv_support<<True
                )

            except Exception as e:
                logger.error(e)

    time.sleep(0.3)
