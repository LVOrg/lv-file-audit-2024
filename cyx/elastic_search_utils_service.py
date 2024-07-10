import typing


class ElasticSearchUtilService:
    def create_privileges(self, privileges_type_from_client:dict)->typing.Tuple[typing.Dict,typing.Dict]:
        """
        Chuyen doi danh sach cac dac quyen do nguoi dung tao sang dang luu tru trong mongodb va elastic search
        Dong thoi ham nay cung update lai danh sach tham khao danh cho giao dien
        Trong Mongodb la 2 ban Privileges, PrivilegesValues
        :param app_name:
        :param privileges_type_from_client:
        :return: (privileges_server,privileges_client)
        """

        privileges_server = {}
        privileges_client = []
        if privileges_type_from_client:

            check_types = dict()
            for x in privileges_type_from_client:
                if check_types.get(x.Type.lower().strip()) is None:
                    privileges_server[x.Type.lower()] = [v.strip() for v in x.Values.lower().split(',')]
                    privileges_client += [{
                        x.Type: x.Values
                    }]
                check_types[x.Type.lower().strip()] = x
        return privileges_server, privileges_client