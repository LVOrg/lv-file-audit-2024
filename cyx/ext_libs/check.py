from vn_word_analyzer import word_analyzer,sentence_analyzer,vn_spell,__clear__
from vn_predicts import predict_accents
# fx= word_analyzer("ngchaooikh")

# fx = sentence_analyzer("ngchaooikh")
# for x in fx:
#     if x.vowel:
#         print(x.provision_word)
print(predict_accents("con meo ma treo cay cau"))
print(predict_accents("tieng viet khong dau"))
print(predict_accents("tet nau banh tet"))
fx = sentence_analyzer("khongphailucnaocungok")

for x in fx:
    print(f"{x.provision_word}->{x.get_vn_suggest_words()}")

