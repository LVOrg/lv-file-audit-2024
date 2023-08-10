from pyvi import ViUtils
import pyvi

# Nhập vào câu tiếng Việt không dấu
sentence = "luat so_huu dat_dai"
from underthesea import word_tokenize
# Chuyển sang tiếng Việt có dấu
fx="TRƯỜNG ĐẠI HOC KHOA HOC HUẾ"
fx= pyvi.ViUtils.remove_accents(fx).decode('utf8')
vietnamese_sentence = ViUtils.add_accents(fx)

# In ra câu tiếng Việt có dấu
print(vietnamese_sentence)
import underthesea

# Nhập vào câu tiếng Việt không dấu
sentence = "tet an banh tet"

# Chuyển sang tiếng Việt có dấu
vietnamese_sentence = word_tokenize("Chuyen tiền k nhận Dc tiên")

# In ra câu tiếng Việt có dấu
print(vietnamese_sentence)