import typing

from textblob import Word

class SpellCorrectorService:
    def __init__(self):
        pass


    def correct(self, text:typing.Optional[str]):
        if text is None:
            return ""
        text = text.replace("  "," ").replace("."," ").replace(","," ")
        words = list(set(text.split(' ')))
        correct_dict = {
            ele: Word(ele).correct() for ele in words
        }
        sentences = text.split(".")
        for k,v in correct_dict.items():
            text = text.replace(k,v)
        return text



