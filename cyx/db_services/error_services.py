import enum
import typing
class DbErrorEnum(enum.Enum):
    db_error = "db_error"
    connection_fail = "connection_fail"
    duplicate="duplicate"
from pymongo.errors import DuplicateKeyError,ConnectionFailure
class DbErrorServices:
    def get_error_code(self, e: typing.Union[DuplicateKeyError,ConnectionFailure])->str|None:
        if isinstance(e,DuplicateKeyError):
            return DbErrorEnum.duplicate.value
        elif isinstance(e,ConnectionFailure):
            return DbErrorEnum.connection_fail.value
        else:
            return DbErrorEnum.db_error.value

    def get_error_fields(self, ex: typing.Union[DuplicateKeyError,ConnectionFailure])->typing.List[str]:
        if isinstance(ex,DuplicateKeyError):
            if isinstance(ex, DuplicateKeyError):
                if hasattr(ex, 'details') and isinstance(ex.details, dict) and isinstance(ex.details.get("keyPattern"),
                                                                                          dict):
                    return list(ex.details["keyPattern"].keys())
        return []

    def get_error_message(self, ex: typing.Union[DuplicateKeyError,ConnectionFailure]):
        if isinstance(ex, DuplicateKeyError):
            return "Data value is existing"
        if isinstance(ex, ConnectionFailure):
            return "Db connection is in error"
        return "Unknown error"
