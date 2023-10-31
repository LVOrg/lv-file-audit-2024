from typing import List
import bson
import datetime
def to_json_convertable(data):
    """
    Sometime Dictionary Data can not portable to Front-End, Such as Dictionary Data contains BSON value.

    The method will fix it. \n
    Đôi khi Dữ liệu từ điển không thể di chuyển sang Front-End, chẳng hạn như Dữ liệu từ điển chứa giá trị BSON.

    Phương pháp sẽ sửa chữa nó.
    :param data:
    :return:
    """
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = to_json_convertable(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [to_json_convertable(x)]
        return ret
    elif isinstance(data, bson.ObjectId):
        return data.__str__()
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    else:
        return data