# import spacy
#
# nlp = spacy.load("vi_core_new_lg")
#
# doc = nlp("Mặc dù có những thách thức, nhưng việc chia nhỏ từ tiếng Việt vẫn có thể được thực hiện")
#
# for token in doc:
#     print(token.text)
from underthesea import word_tokenize
sentence="Mặc dù có những thách thức, nhưng việc chia nhỏ từ tiếng Việt vẫn có thể được thực hiện"
fx = word_tokenize(sentence, format="text")
print(fx)

