import pathlib
import sys

from icecream import ic

sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
from cyx.common import config
if not hasattr(config,"msg_ocr"):
    raise Exception(f"msg_ocr was not found in config")
if not hasattr(config,"app_name"):
    raise Exception(f"app_name was not found in config")
msg_raise_ocr:str = config.msg_ocr
"""
Message wil be raise 
"""
app_name:str =config.app_name
ic(f"app_name={app_name}, msg_ocr={msg_raise_ocr}")
import cy_docs
from cyx.rabbit_utils import Consumer
from cyx.repository import Repository
consumer = Consumer(msg_raise_ocr)
agg_ocr_file = (Repository.files.app(app_name).context.aggregate().match(
  Repository.files.fields.Status==1
).match(
    Repository.files.fields.FileExt=="pdf"
).match(
    ((Repository.files.fields.MsgOCRReRaise ==None)|(Repository.files.fields.MsgOCRReRaise!=msg_raise_ocr))
).sort(
    Repository.files.fields.RegisterOn.desc()
).project(
    cy_docs.fields.upload_id>>Repository.files.fields.id
))

def main():
    ic(agg_ocr_file)
    for x in agg_ocr_file:
        ic(x)
        data = Repository.files.app(app_name).context.find_one(
            Repository.files.fields.id ==x.upload_id
        )
        if not data:
            continue
        data =data.to_json_convertable()
        consumer.raise_message(
            app_name=app_name,
            data =data,
            msg_type=msg_raise_ocr
        )
        Repository.files.app(app_name).context.update(
            Repository.files.fields.id == x.upload_id,
            Repository.files.fields.MsgOCRReRaise<<msg_raise_ocr
        )

if __name__ == "__main__":
    main()