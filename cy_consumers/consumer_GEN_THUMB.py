import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())

__msg__ = pathlib.Path(__file__).stem.split('_')[1].upper()
import cyx.common.msg
import cy_consumers.consumer_base
from cyx.media.image_extractor import ImageExtractorService
class Consumer(cy_consumers.consumer_base.BaseConsumer):
    image_extractor_service = ImageExtractorService()
    def on_message(self,msg:cyx.common.msg.MessageInfo):

        msg_list = list(cyx.common.msg.MSG_MATRIX[msg.Data.get('FileExt','').lower()].keys())
        doc_context = self.docs(msg.AppName)
        app_name = msg.AppName
        upload_data = doc_context.context.find_one(
            doc_context.fields.id==msg.Data["_id"]
        )
        consumer_check_list = upload_data[doc_context.fields.MsgCheckList] or {}
        path_to_file = self.get_physical_path(msg)
        if path_to_file is None:
            self.broker.delete(msg)
            return
        for x in msg_list:
            if (consumer_check_list.get(x) or 0) in [0,1,2]:
                doc_context.context.update(
                    doc_context.fields.id == msg.Data["_id"],
                    getattr(doc_context.fields.MsgCheckList, x) << 1
                )
                list_of_thumbs = []
                default_thumb = self.image_extractor_service.create_thumb(
                    image_file_path=path_to_file,
                    size=700

                )
                list_of_thumbs+=[]
                available_thumbSize = msg.Data.get("AvailableThumbSize",[])
                for x in available_thumbSize:
                    thumb_size =0
                    try:
                        thumb_size= int(x)

                    except:
                        continue
                doc_context.context.update(
                    doc_context.fields.id == msg.Data["_id"],
                    getattr(doc_context.fields.MsgCheckList,x)<<2
                )
                self.set_physical_path(msg,default_thumb)
                self.broker.emit(
                    app_name=app_name,

                )
        # self.broker.delete(msg)
        print(msg_list)

Consumer(__file__)
