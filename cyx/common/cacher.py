__cache__ = {}

import threading



import threading


class CacherService:
    def __init__(self):
        pass

    def get_by_key(self, object_type: str, key: str):
        global __cache__
        if __cache__.get(object_type) is None:
            __cache__[object_type] = {}
        return __cache__[object_type].get(key)

    def add_to_cache(self, object_type: str, key: str, data):
        global __cache__
        if __cache__.get(object_type) is None:
            __cache__[object_type] = {}
        __cache__[object_type][key] = data

    def remove_from_cache(self, object_type: str, key):

        global __cache__
        if __cache__.get(object_type) is None:
            __cache__[object_type] = {}
        if __cache__[object_type].get(key):
            del __cache__[object_type][key]

