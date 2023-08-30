import typing

from cy_vn_suggestion.analyzers import generate_variants, analyzer_words
from cy_vn_suggestion.generators import covert_to_suggestion_ele, generate_suggestions
from cy_vn_suggestion.gram_calculators import calculator_matrix


def suggest(words: str,
            skip_if_in_langs: typing.Optional[typing.List[str]] = None,
            correct_spell: bool = True,
            separate_sticky_words: bool = False):
    if words is None: return ""
    if words == "": return ""
    mat, lens_mat = generate_suggestions(words,
                                         detect_langs=skip_if_in_langs,
                                         correct_spell=correct_spell,
                                         separate_sticky_words=separate_sticky_words)
    ret_mat = calculator_matrix(mat, lens_mat)
    ret = ""
    for x in ret_mat:
        ret += " " + x.OW
    return ret.lstrip(' ')
