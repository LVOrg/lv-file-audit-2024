import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())

__msg__ = pathlib.Path(__file__).stem.split('_')[1].upper()
import cyx.common.msg
import cy_consumers.consumer_base

class Consumer(cy_consumers.consumer_base.BaseConsumer):
    def on_message(self,msg:cyx.common.msg.MessageInfo):

        msg_list = list(cyx.common.msg.MSG_MATRIX[msg.Data.get('FileExt','').lower()].keys())
        doc_context = self.docs(msg.AppName)
        app_name = msg.AppName
        upload_data = doc_context.context.find_one(
            doc_context.fields.id==msg.Data["_id"]
        )
        consumer_check_list = upload_data[doc_context.fields.MsgCheckList] or {}
        for x in msg_list:
            if (consumer_check_list.get(x) or 0) ==0:
                path_to_file = self.get_physical_path_of_main_file_content(msg)
                self.set_physical_path(
                    msg=msg,
                    file_path=path_to_file
                )
                self.broker.emit(
                    app_name=app_name,
                    message_type=x,
                    data=msg.Data

                )
                doc_context.context.update(
                    doc_context.fields.id == msg.Data["_id"],
                    getattr(doc_context.fields.MsgCheckList,x)<<1
                )
        self.broker.delete(msg)
        print(msg_list)

Consumer(__file__)
