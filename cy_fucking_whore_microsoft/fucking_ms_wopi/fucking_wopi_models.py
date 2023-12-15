import typing


class WopiAction:
    app:str
    fav_icon_url:str
    check_license: bool
    name:str
    ext:typing.Optional[str]
    progid:typing.Optional[str]
    is_default: bool
    urlsrc: str
    requires:str
class WopiActionContainer:
    items: typing.List[WopiAction]