def zip_to_dict(data:dict):
    ret = {}
    for k,v in data.items():
        if "." not in k:
            ret[k] = v
        else:
            fks = k.split(".")
            update_dict = ret
            for i in range(len(fks)-1):
                k1= fks[i]
                if update_dict.get(k1) is None:
                    update_dict[k1]=dict()
                    update_dict = update_dict[k1]
                else:
                    update_dict = update_dict[k1]


            update_dict[fks[len(fks)-1]] = v
    return ret