from cy_vn_suggestion.loader import get_config
__config__ = get_config()
def check_word(word: str):
    get_config()
    return __config__.grams_1.get(word)