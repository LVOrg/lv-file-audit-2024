import pathlib
import sys

import numpy
from cy_vn_suggestion.analyzers import  generate_variants, analyzer_words
from cy_vn_suggestion.generators import covert_to_suggestion_ele, generate_suggestions
from cy_vn_suggestion.gram_calculators import calculator_matrix
from cy_vn_suggestion.suggestions import suggest
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
# fx=generate_variants("chicungdothoi")
# for x in fx:
#     print(len(x))
# fx,lens =generate_suggestions("kho thekia macon lamduoc chicungdothoi")
# fx,lens =generate_suggestions("nghile khongThuong")
# fx,lens =generate_suggestions("con ran khong dau")
fx,lens =generate_suggestions("chỉ chừng đó thôi")
ret=calculator_matrix(fx,lens)
print(suggest("chỉ chừng đóthôi"))
print(ret)
"""
[(tiếng,0.00,0.00), (việt,-10.80,4.00), (không,-17.35,0.00), (đầu,-24.70,6.00)]
[(tiếng,0.00,0.00), (việt,-10.80,4.00), (không,-17.35,0.00), (dấu,-26.35,6.00)]
"""