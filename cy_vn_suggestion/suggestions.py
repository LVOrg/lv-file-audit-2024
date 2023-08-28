import typing

from cy_vn_suggestion.analyzers import  generate_variants, analyzer_words
from cy_vn_suggestion.generators import covert_to_suggestion_ele, generate_suggestions
from cy_vn_suggestion.gram_calculators import calculator_matrix
def suggest(words:str, skip_if_in_langs:typing.List[str]=[]):
    mat,lens_mat = generate_suggestions(words,skip_if_in_langs)
    ret_mat = calculator_matrix(mat,lens_mat)
    ret = ""
    for x in ret_mat:
        ret += " "+x.OW
    return ret.lstrip(' ')