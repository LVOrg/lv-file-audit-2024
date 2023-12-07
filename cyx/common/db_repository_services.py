import typing

import cy_kit
from cyx.common.base import (
    DbCollection, DbConnect
)

T = typing.TypeVar("T")


class DbRepository:

    def __init__(self,
                 db_connect=cy_kit.singleton(DbConnect)
                 ):
        self.db_connect = db_connect
        self.admin_db = self.config.admin_db_name

    def get_queryable(self:str, cls: T) -> DbCollection[T]:
        return self.db_connect.db(self.admin_db).doc(cls)
