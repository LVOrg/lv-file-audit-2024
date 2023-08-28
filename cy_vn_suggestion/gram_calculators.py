import typing

from cy_vn_suggestion.loader import get_config
from cy_vn_suggestion.generators import SuggestionElement
from cy_vn_suggestion.utils import get_gram_count
import numpy
import math


def calculator_matrix(matrix: numpy.ndarray, matrix_row_size: typing.List[int]):
    config = get_config()
    len_of_words = len(matrix_row_size)
    numberP = matrix_row_size
    ret =[]


    if len_of_words == 1:
        max = 0
        sure = matrix[0][0].W
        for i in range(numberP[0]):
            possible = matrix[0][i].W
            number1GRam = get_gram_count(possible, config.grams_1)
            if max < number1GRam:
                max = number1GRam
                sure = possible
        ret +=[sure]
        return ret
    else:
        for i1 in range(1, len_of_words):
            recent_possible_num = numberP[i1]
            old_possible_num = numberP[i1 - 1]
            for j in range(recent_possible_num):
                # Q[i1][j] = __config__.MIN
                matrix[i1][j].Q = config.MIN
                temp = config.MIN
                for k1 in range(old_possible_num):
                    # new_word = possible_change[i1][j]

                    # old_word = possible_change[i1 - 1][k1]
                    new_word,old_word  = matrix[i1][j].W, matrix[i1-1][k1].W
                    log = -100.0

                    number2Gram = get_gram_count(old_word + " " + new_word, config.grams_2)
                    number1Gram = get_gram_count(old_word, config.grams_1)
                    if number1Gram > 0 and number2Gram > 0:
                        log = math.log((number2Gram + 1) / (number1Gram + config.statistic[old_word]))
                    else:
                        log = math.log(1.0 / (2 * (config.size_2_grams + config.total_count_2_grams)))

                    if i1 == 1:
                        log += math.log(
                            (number1Gram + 1) / (config.size_1_gram + config.total_count_1_gram))
                    if temp != matrix[i1 - 1][k1].Q:
                        if temp == config.MIN:
                            temp = matrix[i1 - 1][k1].Q
                    value = matrix[i1 - 1][k1].Q + log

                    if matrix[i1][j].Q < value:
                        # print(f"{old_word} {new_word} -> {value}")
                        matrix[i1][j].Q = value
                        matrix[i1][j].trace = k1
        max = config.MIN
        k = 0

        for l in range(numberP[len_of_words - 1]):
            if max <= matrix[len_of_words - 1][l].Q:
                max = matrix[len_of_words - 1][l].Q
                k = l
        result = [matrix[len_of_words - 1][k]]
        k = matrix[len_of_words - 1][k].trace
        i = len_of_words - 2
        while i >= 0 and matrix[i][k]:
            result = [matrix[i][k]] + result
            k = matrix[i][k].trace
            i = i - 1

    return result


