import os
import pathlib
import typing
import re
from underthesea import word_tokenize



class VnSegmenterService:
    def __init__(self):

        self.word_tokenize = word_tokenize
    def parse_word_segment(self, content: str,boot: typing.List[float]=None,clears: typing.List[str]=None) -> str:
        if content is None:
            return ""
        elif content == "" or content.lstrip(' ').rstrip(' ')=='':
            return ""
        clear_content = content
        clear_content = re.sub(' +', ' ', clear_content)
        if boot:
            clears =[".",":","/","\\","!",'?','@','#','@','^','&','*','(',')','+','-','*','/','%']
        if clears is not None:
            for x in clears:
                clear_content = clear_content.replace(x," ")
        clear_content = re.sub(' +', ' ', clear_content)
        if boot is None:
            clear_content = ('.'+clear_content+'.').replace(".", " . ").replace(",", " , ")
            clear_content = re.sub(' +', ' ', clear_content)
            ret = "".join(self.word_tokenize(clear_content)).lstrip('. ').rstrip(' .')
            return ret
        else:
            """
                        'query':"(\"quy_trình phần_mềm kiểm_thử\") OR (quy_trình^2 phần_mềm^2 kiểm_thử^2)"
                        """
            clear_content = re.sub(' +', ' ', clear_content)
            clear_content = ('.' + clear_content + '.').replace(".", " . ").replace(",", " , ")
            ret = clear_content
            if clear_content!="":
                ret = " ".join(self.word_tokenize(clear_content))
            boot_index = 0
            ret_x = ""
            start =0
            word_count =0
            for x in ret:
                if x==" ":
                    word_count += 1
                if x =='_':
                    start +=1
                if x==" ":
                    if start>0:

                        ret_x+=f"^{start+1}"
                        boot_index = (boot_index+1) % len(boot)
                        start = 0
                ret_x += x
            return f'(\\"{ret.rstrip(" ")}\\")^{word_count} OR ({ret_x.rstrip(" ")})'

