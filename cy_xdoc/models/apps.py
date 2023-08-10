import typing
from datetime import datetime
import cy_docs
from bson import ObjectId
@cy_docs.define(
    name="sys_applications",
    uniques=["Name","NameLower","Email"],
    indexes=["Domain","LoginUrl","ReturnUrlAfterSignIn"]
)
class App:
    import bson
    _id:str
    Name:str
    NameLower:str
    """
    Để cho truy cập nhanh dùng NameLower so sánh với giá trị lower
    """
    RegisteredBy:str
    RegisteredOn:datetime
    ModifiedOn:datetime
    Domain:str
    LoginUrl:str
    SecretKey:str
    ReturnUrlAfterSignIn:str
    ReturnSegmentKey:str
    Description:str
    Email:str
    Username:str
    Password:str
    SecretKey:str
    """
    Email dùng để liên lạc với application khi cần. Ví dụ dùng trong trường ho75ptruy tìm lại mật khẩu của user root trên app
    """

    LatestAccess: typing.Optional[datetime]
    """
    Latest access time
    """
    AccessCount: typing.Optional[int]
    Stats: typing.Optional[dict]
    """
    Stat of app
    """



class AppStatsDimension:
    TotalFiles: int
    """
    Amount of  files which were uploaded 
    """
    TotalFilesStillUploading: int
    """
    Amount of  files which is still uploading 
    """
    TotalSizeOfFilesUploadedInGB: float
    """
    Total size of files were uploaded
    """
    TotalSizeOfFilesStillUploadingInGB: float
    """
    Total size of files were uploaded
    """
    TotalAmountInGB: float

class AppStatsYear(AppStatsDimension):
    Year: int
class AppStatsMonth(AppStatsYear):
    Month:int
class AppStatsDay(AppStatsMonth):
    Day:int
@cy_docs.define(
    name="app_stats",
    uniques=["AppName","AppName"]
)
class AppStats:
    _id: str
    AppName: str
    AppName:str
    AppId: str
    YearStat: typing.Optional[AppStatsYear]
    MonthStat: typing.Optional[AppStatsMonth]
    DayStat : typing.Optional[AppStatsDay]
    Grand : typing.Optional[AppStatsDimension]
    """
    Total till now
    """




