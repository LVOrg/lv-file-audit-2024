from cy_vn_suggestion.suggestions import suggest
from cy_es import cy_es_manager

if __name__ == "__main__":
    txt = suggest("can cứ tình hình hoat dong thuc te va tra luong tai cac chi nhanh",correct_spell=False)
    print(txt)
    txt = suggest("hom nay toi di hoc")
    print(txt)
    txt = suggest("bao cao tai chinh nam 2024 cua vietlott",correct_spell=False)
    print(txt)
    txt = suggest("10 dong du lieu",correct_spell=False)
    print(txt)
    txt = suggest("so tien la 1000 dong", correct_spell=False)
    print(txt)