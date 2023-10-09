__version__ = "0.0.0.0"
import phunspell
vn_spell = phunspell.Phunspell("vi_VN")
from cy_vn_suggestion.suggestions import suggest, correct_word