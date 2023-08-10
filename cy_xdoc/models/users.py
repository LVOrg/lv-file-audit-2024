from datetime import datetime
import cy_docs
from bson import ObjectId
@cy_docs.define(
    name="sys_users",
    uniques=["Username","Email","UsernameLowerCase","HashPassword"]
)
class User:
    _id: ObjectId
    Username:str
    UsernameLowerCase:str
    Password:str
    HashPassword:str
    PasswordSalt:str
    Email:str
    LoginCount:int
    """
    Số lần login
    """
    LastestPasswordChangeOn:datetime
    """
    Lần cuối sửa mật khẩu
    """
    Application:str
    CreatedOn: datetime
    IsLocked: bool
    LockedOn : datetime
    CreatedOnUTC:datetime
    IsSysAdmin:bool