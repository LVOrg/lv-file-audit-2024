import pathlib
import sys

import numpy
from cy_vn_suggestion.analyzers import  generate_variants, analyzer_words
from cy_vn_suggestion.generators import covert_to_suggestion_ele, generate_suggestions
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
# fx=generate_variants("chicungdothoi")
# for x in fx:
#     print(len(x))
fx =generate_suggestions("kho thekia macon lamduoc chicungdothoi")
class SuggestionElement:
    word: str
    quality: float

    def __init__(self, word: str, quality: float):
        self.quality = quality
        self.word = word


fx = numpy.empty((10,20),dtype=SuggestionElement)

fx[0:0]=SuggestionElement("A",1)
print(fx)