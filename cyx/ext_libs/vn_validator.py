__full_accents__ = (f"UÙÚỦỤŨƯỪỨỬỰỮ"
                    f"eèéẻẹẽêềếểệễ"
                    f"oòóỏọõôồốổộỗơờớởợỡ"
                    f"OÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ"
                    f"uùúủụũưừứửựữ"
                    f"aàáảạãâầấẩậẫăằắẳặẵ"
                    f"AÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ"
                    f"iìíỉịĩ"
                    f"EÈÉẺẸẼÊỀẾỂỆỄ"
                    f"YỲÝỶỴỸ"
                    f"IÌÍỈỊĨ"
                    f"yỳýỷỵỹ")
def is_vn_word(word:str):
    if word[0]=='z': return False
    if word[0] == 'Z': return False
    index = 0
    pre_index_of_vowel = -1
    for x in word:
        if x in __full_accents__:
            if index>-1 and word[index-1]==x:
                return False
            if  pre_index_of_vowel>-1 and index-pre_index_of_vowel>1:
                return False
            pre_index_of_vowel = index
        index +=1

    return pre_index_of_vowel>-1



