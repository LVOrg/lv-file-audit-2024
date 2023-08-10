import re
import typing


class TextProcessService:
    def __init__(self):
        self.patterns_vn = {
            '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
            '[đ]': 'd',
            '[èéẻẽẹêềếểễệ]': 'e',
            '[ìíỉĩị]': 'i',
            '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
            '[ùúủũụưừứửữự]': 'u',
            '[ỳýỷỹỵ]': 'y'}

    def vn_clear_accent_mark(self, content: typing.Optional[str]):
        """
            Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
            text: input string to be converted
            Return: string converted
            """
        content = content or ''
        output = content
        for regex, replace in self.patterns_vn.items():
            try:
                output = re.sub(regex, replace, output)
                # deal with upper case
                output = re.sub(regex.upper(), replace.upper(), output)
            except Exception as e:
                fx=1
        return output
