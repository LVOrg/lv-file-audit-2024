import enum
import os.path
import pathlib
import typing
import mimetypes

import cy_docs
import cyx.common.msg
from cyx.common import config


class ContentTypeEnum(enum.Enum):
    Video = 5
    Image = 4
    Office = 3
    Pdf = 1
    Unknown = 0


from cyx.common import config


class ContentService:
    def __init__(self):
        self.file_storage_path = config.file_storage_path
        self.s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
        self.s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
        self.rdrsegment = None  # RDRSegmenter.RDRSegmenter()
        self.tokenizer = None  # Tokenizer.Tokenizer()

    def get_type(self, msg_data: typing.Union[dict, cy_docs.DocumentObject]) -> ContentTypeEnum:
        data = msg_data
        if isinstance(data, cy_docs.DocumentObject):
            data = data.to_json_convertable()
        ret = ContentTypeEnum.Unknown

        file_ext = data["FileExt"]
        if not file_ext:
            main_file_id = data["MainFileId"]
            if isinstance(main_file_id, str) and "://" in main_file_id:
                file_ext = pathlib.Path(main_file_id.split("://")[1]).suffix
                if file_ext == "":
                    return ContentTypeEnum.Unknown
                else:
                    file_ext = file_ext[1:]
                    if file_ext == "pdf":
                        return ContentTypeEnum.Pdf
                    elif file_ext in config.ext_office_file:
                        return ContentTypeEnum.Office
                    elif file_ext == "avif":
                        return ContentTypeEnum.Image
                    else:
                        mt, _ = mimetypes.guess_type(f"a.{file_ext}")
                        if mt.startswith("image/"):
                            return ContentTypeEnum.Image
                        elif mt.startswith("video/"):
                            return ContentTypeEnum.Video

        elif file_ext == "pdf":
            return ContentTypeEnum.Pdf
        elif file_ext in config.ext_office_file:
            return ContentTypeEnum.Office
        elif file_ext == "avif":
            return ContentTypeEnum.Image
        else:
            mt, _ = mimetypes.guess_type(f"a.{file_ext}")
            if mt.startswith("image/"):
                return ContentTypeEnum.Image
            elif mt.startswith("video/"):
                return ContentTypeEnum.Video
        return ContentTypeEnum.Unknown

    def get_master_resource(self, msg_info: cyx.common.msg.MessageInfo):
        data = msg_info.Data
        if isinstance(data, cy_docs.DocumentObject):
            data = data.to_json_convertable()
        main_file_id = data["MainFileId"]
        if isinstance(main_file_id, str) and "://" in main_file_id:
            rel_path = main_file_id.split("://")[1]
            real_file_path = os.path.join(self.file_storage_path, rel_path)
            return real_file_path
        return None

    def get_resource(self, msg_info: cyx.common.msg.MessageInfo):
        if isinstance(msg_info.resource, str):
            return msg_info.resource
        data = msg_info.Data
        if isinstance(data, cy_docs.DocumentObject):
            data = data.to_json_convertable()
        main_file_id = data["MainFileId"]
        if isinstance(main_file_id, str) and "://" in main_file_id:
            rel_path = main_file_id.split("://")[1]
            real_file_path = os.path.join(self.file_storage_path, rel_path)
            return real_file_path
        return None

    def well_form_text(self, text):
        if isinstance(text, str):
            ret = text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ').replace('\n', ' ').replace('\t',
                                                                                                              ' ').replace(
                '\r', ' ').replace("  ", ' ').rstrip(' ').lstrip(' ')
            ret_remove_accents = self.remove_accents(ret)
            # self.rdrsegment.segmentRawSentences(self.tokenizer, ret)
            if ret_remove_accents!=ret:
                ret = ret + " " + ret_remove_accents
            return ret
        return ""

    def remove_accents(self, input_str):
        if not isinstance(input_str, str):
            return ""

        s = ''
        for c in input_str:
            if c in self.s1:
                s += self.s0[self.s1.index(c)]
            else:
                s += c
        return s

    def create_content_file(self, master_resource, content: str):
        if not os.path.isfile(master_resource):
            return None
        content_dir_path = os.path.join(pathlib.Path(master_resource).parent.__str__(), "content")
        os.makedirs(content_dir_path, exist_ok=True)
        content_file_path = os.path.join(content_dir_path, "context.txt")
        if os.path.isfile(content_file_path):
            return content_file_path
        with open(content_file_path, "wb") as fs:
            fs.write(content.encode('utf8'))
        return content_file_path
