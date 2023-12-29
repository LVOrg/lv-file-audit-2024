import gc
import mimetypes
import pathlib
import time
import os
from yaml import SafeDumper
import typing
mime_data = {}
mime_data[".323"] = "text/h323"
mime_data[".3g2"] = "video/3gpp2"
mime_data[".3gp2"] = "video/3gpp2"
mime_data[".3gp"] = "video/3gpp"
mime_data[".3gpp"] = "video/3gpp"
mime_data[".aaf"] = "application/octet-stream"
mime_data[".aac"] = "audio/aac"
mime_data[".aca"] = "application/octet-stream"
mime_data[".accdb"] = "application/msaccess"
mime_data[".accde"] = "application/msaccess"
mime_data[".accdt"] = "application/msaccess"
mime_data[".acx"] = "application/internet-property-stream"
mime_data[".adt"] = "audio/vnd.dlna.adts"
mime_data[".adts"] = "audio/vnd.dlna.adts"
mime_data[".afm"] = "application/octet-stream"
mime_data[".ai"] = "application/postscript"
mime_data[".aif"] = "audio/x-aiff"
mime_data[".aifc"] = "audio/aiff"
mime_data[".aiff"] = "audio/aiff"
mime_data[".application"] = "application/x-ms-application"
mime_data[".art"] = "image/x-jg"
mime_data[".asd"] = "application/octet-stream"
mime_data[".asf"] = "video/x-ms-asf"
mime_data[".asi"] = "application/octet-stream"
mime_data[".asm"] = "text/plain"
mime_data[".asr"] = "video/x-ms-asf"
mime_data[".asx"] = "video/x-ms-asf"
mime_data[".atom"] = "application/atom+xml"
mime_data[".au"] = "audio/basic"
mime_data[".avi"] = "video/avi"
mime_data[".axs"] = "application/olescript"
mime_data[".bas"] = "text/plain"
mime_data[".bcpio"] = "application/x-bcpio"
mime_data[".bin"] = "application/octet-stream"
mime_data[".bmp"] = "image/bmp"
mime_data[".c"] = "text/plain"
mime_data[".cab"] = "application/vnd.ms-cab-compressed"
mime_data[".calx"] = "application/vnd.ms-office.calx"
mime_data[".cat"] = "application/vnd.ms-pki.seccat"
mime_data[".cdf"] = "application/x-cdf"
mime_data[".chm"] = "application/octet-stream"
mime_data[".class"] = "application/x-java-applet"
mime_data[".clp"] = "application/x-msclip"
mime_data[".cmx"] = "image/x-cmx"
mime_data[".cnf"] = "text/plain"
mime_data[".cod"] = "image/cis-cod"
mime_data[".cpio"] = "application/x-cpio"
mime_data[".cpp"] = "text/plain"
mime_data[".crd"] = "application/x-mscardfile"
mime_data[".crl"] = "application/pkix-crl"
mime_data[".crt"] = "application/x-x509-ca-cert"
mime_data[".csh"] = "application/x-csh"
mime_data[".css"] = "text/css"
mime_data[".csv"] = "application/octet-stream"
mime_data[".cur"] = "application/octet-stream"
mime_data[".dcr"] = "application/x-director"
mime_data[".deploy"] = "application/octet-stream"
mime_data[".der"] = "application/x-x509-ca-cert"
mime_data[".dib"] = "image/bmp"
mime_data[".dir"] = "application/x-director"
mime_data[".disco"] = "text/xml"
mime_data[".dll"] = "application/x-msdownload"
mime_data[".dll.configuration"] = "text/xml"
mime_data[".dlm"] = "text/dlm"
mime_data[".doc"] = "application/msword"
mime_data[".docm"] = "application/vnd.ms-word.document.macroEnabled.12"
mime_data[".docx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
mime_data[".dot"] = "application/msword"
mime_data[".dotm"] = "application/vnd.ms-word.template.macroEnabled.12"
mime_data[".dotx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.template"
mime_data[".dsp"] = "application/octet-stream"
mime_data[".dtd"] = "text/xml"
mime_data[".dvi"] = "application/x-dvi"
mime_data[".dvr-ms"] = "video/x-ms-dvr"
mime_data[".dwf"] = "drawing/x-dwf"
mime_data[".dwp"] = "application/octet-stream"
mime_data[".dxr"] = "application/x-director"
mime_data[".eml"] = "message/rfc822"
mime_data[".emz"] = "application/octet-stream"
mime_data[".eot"] = "application/vnd.ms-fontobject"
mime_data[".eps"] = "application/postscript"
mime_data[".etx"] = "text/x-setext"
mime_data[".evy"] = "application/envoy"
mime_data[".exe"] = "application/octet-stream"
mime_data[".exe.configuration"] = "text/xml"
mime_data[".fdf"] = "application/vnd.fdf"
mime_data[".fif"] = "application/fractals"
mime_data[".fla"] = "application/octet-stream"
mime_data[".flr"] = "x-world/x-vrml"
mime_data[".flv"] = "video/x-flv"
mime_data[".gif"] = "image/gif"
mime_data[".gtar"] = "application/x-gtar"
mime_data[".gz"] = "application/x-gzip"
mime_data[".h"] = "text/plain"
mime_data[".hdf"] = "application/x-hdf"
mime_data[".hdml"] = "text/x-hdml"
mime_data[".hhc"] = "application/x-oleobject"
mime_data[".hhk"] = "application/octet-stream"
mime_data[".hhp"] = "application/octet-stream"
mime_data[".hlp"] = "application/winhlp"
mime_data[".hqx"] = "application/mac-binhex40"
mime_data[".hta"] = "application/hta"
mime_data[".htc"] = "text/x-component"
mime_data[".htm"] = "text/html"
mime_data[".html"] = "text/html"
mime_data[".htt"] = "text/webviewhtml"
mime_data[".hxt"] = "text/html"
mime_data[".ico"] = "image/x-icon"
mime_data[".ics"] = "text/calendar"
mime_data[".ief"] = "image/ief"
mime_data[".iii"] = "application/x-iphone"
mime_data[".inf"] = "application/octet-stream"
mime_data[".ins"] = "application/x-internet-signup"
mime_data[".isp"] = "application/x-internet-signup"
mime_data[".IVF"] = "video/x-ivf"
mime_data[".jar"] = "application/java-archive"
mime_data[".java"] = "application/octet-stream"
mime_data[".jck"] = "application/liquidmotion"
mime_data[".jcz"] = "application/liquidmotion"
mime_data[".jfif"] = "image/pjpeg"
mime_data[".jpb"] = "application/octet-stream"
mime_data[".jpe"] = "image/jpeg"
mime_data[".jpeg"] = "image/jpeg"
mime_data[".jpg"] = "image/jpeg"
mime_data[".js"] = "application/javascript"
mime_data[".json"] = "application/json"
mime_data[".jsx"] = "application/javascrip"
mime_data[".latex"] = "application/x-latex"
mime_data[".lit"] = "application/x-ms-reader"
mime_data[".lpk"] = "application/octet-stream"
mime_data[".lsf"] = "video/x-la-asf"
mime_data[".lsx"] = "video/x-la-asf"
mime_data[".lzh"] = "application/octet-stream"
mime_data[".m13"] = "application/x-msmediaview"
mime_data[".m14"] = "application/x-msmediaview"
mime_data[".m1v"] = "video/mpeg"
mime_data[".m2ts"] = "video/vnd.dlna.mpeg-tts"
mime_data[".m3u"] = "audio/x-mpegurl"
mime_data[".m4a"] = "audio/mp4"
mime_data[".m4v"] = "video/mp4"
mime_data[".man"] = "application/x-troff-man"
mime_data[".manifest"] = "application/x-ms-manifest"
mime_data[".map"] = "text/plain"
mime_data[".mdb"] = "application/x-msaccess"
mime_data[".mdp"] = "application/octet-stream"
mime_data[".me"] = "application/x-troff-me"
mime_data[".mht"] = "message/rfc822"
mime_data[".mhtml"] = "message/rfc822"
mime_data[".mid"] = "audio/mid"
mime_data[".midi"] = "audio/mid"
mime_data[".mix"] = "application/octet-stream"
mime_data[".mmf"] = "application/x-smaf"
mime_data[".mno"] = "text/xml"
mime_data[".mny"] = "application/x-msmoney"
mime_data[".mov"] = "video/quicktime"
mime_data[".movie"] = "video/x-sgi-movie"
mime_data[".mp2"] = "video/mpeg"
mime_data[".mp3"] = "audio/mpeg"
mime_data[".mp4"] = "video/mp4"
mime_data[".mp4v"] = "video/mp4"
mime_data[".mpa"] = "video/mpeg"
mime_data[".mpe"] = "video/mpeg"
mime_data[".mpeg"] = "video/mpeg"
mime_data[".mpg"] = "video/mpeg"
mime_data[".mpp"] = "application/vnd.ms-project"
mime_data[".mpv2"] = "video/mpeg"
mime_data[".ms"] = "application/x-troff-ms"
mime_data[".msi"] = "application/octet-stream"
mime_data[".mso"] = "application/octet-stream"
mime_data[".mvb"] = "application/x-msmediaview"
mime_data[".mvc"] = "application/x-miva-compiled"
mime_data[".nc"] = "application/x-netcdf"
mime_data[".nsc"] = "video/x-ms-asf"
mime_data[".nws"] = "message/rfc822"
mime_data[".ocx"] = "application/octet-stream"
mime_data[".oda"] = "application/oda"
mime_data[".odc"] = "text/x-ms-odc"
mime_data[".ods"] = "application/oleobject"
mime_data[".oga"] = "audio/ogg"
mime_data[".ogg"] = "video/ogg"
mime_data[".ogv"] = "video/ogg"
mime_data[".one"] = "application/onenote"
mime_data[".onea"] = "application/onenote"
mime_data[".onetoc"] = "application/onenote"
mime_data[".onetoc2"] = "application/onenote"
mime_data[".onetmp"] = "application/onenote"
mime_data[".onepkg"] = "application/onenote"
mime_data[".osdx"] = "application/opensearchdescription+xml"
mime_data[".otf"] = "font/otf"
mime_data[".p10"] = "application/pkcs10"
mime_data[".p12"] = "application/x-pkcs12"
mime_data[".p7b"] = "application/x-pkcs7-certificates"
mime_data[".p7c"] = "application/pkcs7-mime"
mime_data[".p7m"] = "application/pkcs7-mime"
mime_data[".p7r"] = "application/x-pkcs7-certreqresp"
mime_data[".p7s"] = "application/pkcs7-signature"
mime_data[".pbm"] = "image/x-portable-bitmap"
mime_data[".pcx"] = "application/octet-stream"
mime_data[".pcz"] = "application/octet-stream"
mime_data[".pdf"] = "application/pdf"
mime_data[".pfb"] = "application/octet-stream"
mime_data[".pfm"] = "application/octet-stream"
mime_data[".pfx"] = "application/x-pkcs12"
mime_data[".pgm"] = "image/x-portable-graymap"
mime_data[".pko"] = "application/vnd.ms-pki.pko"
mime_data[".pma"] = "application/x-perfmon"
mime_data[".pmc"] = "application/x-perfmon"
mime_data[".pml"] = "application/x-perfmon"
mime_data[".pmr"] = "application/x-perfmon"
mime_data[".pmw"] = "application/x-perfmon"
mime_data[".png"] = "image/png"
mime_data[".pnm"] = "image/x-portable-anymap"
mime_data[".pnz"] = "image/png"
mime_data[".pot"] = "application/vnd.ms-powerpoint"
mime_data[".potm"] = "application/vnd.ms-powerpoint.template.macroEnabled.12"
mime_data[".potx"] = "application/vnd.openxmlformats-officedocument.presentationml.template"
mime_data[".ppam"] = "application/vnd.ms-powerpoint.addin.macroEnabled.12"
mime_data[".ppm"] = "image/x-portable-pixmap"
mime_data[".pps"] = "application/vnd.ms-powerpoint"
mime_data[".ppsm"] = "application/vnd.ms-powerpoint.slideshow.macroEnabled.12"
mime_data[".ppsx"] = "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
mime_data[".ppt"] = "application/vnd.ms-powerpoint"
mime_data[".pptm"] = "application/vnd.ms-powerpoint.presentation.macroEnabled.12"
mime_data[".pptx"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
mime_data[".prf"] = "application/pics-rules"
mime_data[".prm"] = "application/octet-stream"
mime_data[".prx"] = "application/octet-stream"
mime_data[".ps"] = "application/postscript"
mime_data[".psd"] = "application/octet-stream"
mime_data[".psm"] = "application/octet-stream"
mime_data[".psp"] = "application/octet-stream"
mime_data[".pub"] = "application/x-mspublisher"
mime_data[".qt"] = "video/quicktime"
mime_data[".qtl"] = "application/x-quicktimeplayer"
mime_data[".qxd"] = "application/octet-stream"
mime_data[".ra"] = "audio/x-pn-realaudio"
mime_data[".ram"] = "audio/x-pn-realaudio"
mime_data[".rar"] = "application/octet-stream"
mime_data[".ras"] = "image/x-cmu-raster"
mime_data[".rf"] = "image/vnd.rn-realflash"
mime_data[".rgb"] = "image/x-rgb"
mime_data[".rm"] = "application/vnd.rn-realmedia"
mime_data[".rmi"] = "audio/mid"
mime_data[".roff"] = "application/x-troff"
mime_data[".rpm"] = "audio/x-pn-realaudio-plugin"
mime_data[".rtf"] = "application/rtf"
mime_data[".rtx"] = "text/richtext"
mime_data[".scd"] = "application/x-msschedule"
mime_data[".sct"] = "text/scriptlet"
mime_data[".sea"] = "application/octet-stream"
mime_data[".setpay"] = "application/set-payment-initiation"
mime_data[".setreg"] = "application/set-registration-initiation"
mime_data[".sgml"] = "text/sgml"
mime_data[".sh"] = "application/x-sh"
mime_data[".shar"] = "application/x-shar"
mime_data[".sit"] = "application/x-stuffit"
mime_data[".sldm"] = "application/vnd.ms-powerpoint.slide.macroEnabled.12"
mime_data[".sldx"] = "application/vnd.openxmlformats-officedocument.presentationml.slide"
mime_data[".smd"] = "audio/x-smd"
mime_data[".smi"] = "application/octet-stream"
mime_data[".smx"] = "audio/x-smd"
mime_data[".smz"] = "audio/x-smd"
mime_data[".snd"] = "audio/basic"
mime_data[".snp"] = "application/octet-stream"
mime_data[".spc"] = "application/x-pkcs7-certificates"
mime_data[".spl"] = "application/futuresplash"
mime_data[".spx"] = "audio/ogg"
mime_data[".src"] = "application/x-wais-source"
mime_data[".ssm"] = "application/streamingmedia"
mime_data[".sst"] = "application/vnd.ms-pki.certstore"
mime_data[".stl"] = "application/vnd.ms-pki.stl"
mime_data[".sv4cpio"] = "application/x-sv4cpio"
mime_data[".sv4crc"] = "application/x-sv4crc"
mime_data[".svg"] = "image/svg+xml"
mime_data[".svgz"] = "image/svg+xml"
mime_data[".swf"] = "application/x-shockwave-flash"
mime_data[".t"] = "application/x-troff"
mime_data[".tar"] = "application/x-tar"
mime_data[".tcl"] = "application/x-tcl"
mime_data[".tex"] = "application/x-tex"
mime_data[".texi"] = "application/x-texinfo"
mime_data[".texinfo"] = "application/x-texinfo"
mime_data[".tgz"] = "application/x-compressed"
mime_data[".thmx"] = "application/vnd.ms-officetheme"
mime_data[".thn"] = "application/octet-stream"
mime_data[".tif"] = "image/tiff"
mime_data[".tiff"] = "image/tiff"
mime_data[".toc"] = "application/octet-stream"
mime_data[".tr"] = "application/x-troff"
mime_data[".trm"] = "application/x-msterminal"
mime_data[".ts"] = "video/vnd.dlna.mpeg-tts"
mime_data[".tsv"] = "text/tab-separated-values"
mime_data[".ttf"] = "application/octet-stream"
mime_data[".tts"] = "video/vnd.dlna.mpeg-tts"
mime_data[".txt"] = "text/plain"
mime_data[".u32"] = "application/octet-stream"
mime_data[".uls"] = "text/iuls"
mime_data[".ustar"] = "application/x-ustar"
mime_data[".vbs"] = "text/vbscript"
mime_data[".vcf"] = "text/x-vcard"
mime_data[".vcs"] = "text/plain"
mime_data[".vdx"] = "application/vnd.ms-visio.viewer"
mime_data[".vml"] = "text/xml"
mime_data[".vsd"] = "application/vnd.visio"
mime_data[".vss"] = "application/vnd.visio"
mime_data[".vst"] = "application/vnd.visio"
mime_data[".vsto"] = "application/x-ms-vsto"
mime_data[".vsw"] = "application/vnd.visio"
mime_data[".vsx"] = "application/vnd.visio"
mime_data[".vtx"] = "application/vnd.visio"
mime_data[".wav"] = "audio/wav"
mime_data[".wax"] = "audio/x-ms-wax"
mime_data[".wbmp"] = "image/vnd.wap.wbmp"
mime_data[".wcm"] = "application/vnd.ms-works"
mime_data[".wdb"] = "application/vnd.ms-works"
mime_data[".webm"] = "video/webm"
mime_data[".wks"] = "application/vnd.ms-works"
mime_data[".wm"] = "video/x-ms-wm"
mime_data[".wma"] = "audio/x-ms-wma"
mime_data[".wmd"] = "application/x-ms-wmd"
mime_data[".wmf"] = "application/x-msmetafile"
mime_data[".wml"] = "text/vnd.wap.wml"
mime_data[".wmlc"] = "application/vnd.wap.wmlc"
mime_data[".wmls"] = "text/vnd.wap.wmlscript"
mime_data[".wmlsc"] = "application/vnd.wap.wmlscriptc"
mime_data[".wmp"] = "video/x-ms-wmp"
mime_data[".wmv"] = "video/x-ms-wmv"
mime_data[".wmx"] = "video/x-ms-wmx"
mime_data[".wmz"] = "application/x-ms-wmz"
mime_data[".woff"] = "font/x-woff"
mime_data[".wps"] = "application/vnd.ms-works"
mime_data[".wri"] = "application/x-mswrite"
mime_data[".wrl"] = "x-world/x-vrml"
mime_data[".wrz"] = "x-world/x-vrml"
mime_data[".wsdl"] = "text/xml"
mime_data[".wtv"] = "video/x-ms-wtv"
mime_data[".wvx"] = "video/x-ms-wvx"
mime_data[".x"] = "application/directx"
mime_data[".xaf"] = "x-world/x-vrml"
mime_data[".xaml"] = "application/xaml+xml"
mime_data[".xap"] = "application/x-silverlight-app"
mime_data[".xbap"] = "application/x-ms-xbap"
mime_data[".xbm"] = "image/x-xbitmap"
mime_data[".xdr"] = "text/plain"
mime_data[".xht"] = "application/xhtml+xml"
mime_data[".xhtml"] = "application/xhtml+xml"
mime_data[".xla"] = "application/vnd.ms-excel"
mime_data[".xlam"] = "application/vnd.ms-excel.addin.macroEnabled.12"
mime_data[".xlc"] = "application/vnd.ms-excel"
mime_data[".xlm"] = "application/vnd.ms-excel"
mime_data[".xls"] = "application/vnd.ms-excel"
mime_data[".xlsb"] = "application/vnd.ms-excel.sheet.binary.macroEnabled.12"
mime_data[".xlsm"] = "application/vnd.ms-excel.sheet.macroEnabled.12"
mime_data[".xlsx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
mime_data[".xlt"] = "application/vnd.ms-excel"
mime_data[".xltm"] = "application/vnd.ms-excel.template.macroEnabled.12"
mime_data[".xltx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.template"
mime_data[".xlw"] = "application/vnd.ms-excel"
mime_data[".xml"] = "text/xml"
mime_data[".xof"] = "x-world/x-vrml"
mime_data[".xpm"] = "image/x-xpixmap"
mime_data[".xps"] = "application/vnd.ms-xpsdocument"
mime_data[".xsd"] = "text/xml"
mime_data[".xsf"] = "text/xml"
mime_data[".xsl"] = "text/xml"
mime_data[".xslt"] = "text/xml"
mime_data[".xsn"] = "application/octet-stream"
mime_data[".xtp"] = "application/octet-stream"
mime_data[".xwd"] = "image/x-xwindowdump"
mime_data[".z"] = "application/x-compress"
mime_data[".zip"] = "application/x-zip-compressed"
# ------------------audio-------------------------
mime_data[".weba"] = "audio/webm"

# ----Image ---------------------------------
mime_data[".webp"] = "image/webp"
mime_data[".avif"] = "image/avif"

mimetypes.types_map = {**mime_data, **mimetypes.types_map}
__old__ = mimetypes.guess_type


def __new__fn__(url, strict=True):

    items = url.split('.')
    item = "." + items[items.__len__() - 1]
    a, b = mime_data.get(item), None
    if a is None:
        a, b = __old__(url, strict)
    if a is None:
        x = os.path.splitext(url)[1]
        a = mime_data.get(x)
        if a is None:
            a = r'application/octet-stream'
    return a, b


mimetypes.guess_type = __new__fn__
"""
all re definre hear
"""

from fastapi.middleware.cors import CORSMiddleware

import logging
from fastapi.exceptions import HTTPException
from typing import List
import typing
import uvicorn
import jose
from jose import JWTError, jwt
import threading
from datetime import datetime
import inspect
import fastapi
import pydantic
from fastapi.staticfiles import StaticFiles

__wrap_pydantic_cache__ = {}
__wrap_pydantic_lock__ = threading.Lock()


def get_cls(cls):
    if sys.modules.get(cls.__module__):
        mdl = sys.modules[cls.__module__]
        if not hasattr(cls, "__name__"):
            return
        if hasattr(mdl, cls.__name__):
            ret = getattr(mdl, cls.__name__)
            if issubclass(ret, pydantic.BaseModel):
                return ret


def __wrap_pydantic__(pre, cls, is_lock=True):
    global __wrap_pydantic_cache__
    global __wrap_pydantic_lock__
    if cls.__module__ == typing.__name__ and cls.__origin__ == list:
        ret = []
        for x in cls.__args__:
            ret += [__wrap_pydantic__("", x)]
        cls.__args__ = tuple(ret)
        return cls
    if __wrap_pydantic_cache__.get(f"{cls.__module__}/{cls.__name__}") and is_lock:
        return __wrap_pydantic_cache__.get(f"{cls.__module__}/{cls.__name__}")

    if hasattr(cls, "__origin__"):
        print(cls)
    if hasattr(cls, "__annotations__"):
        ls = list(cls.__dict__.items())
        for k, v in ls:
            if not (k[0:2] == "__" and k[:-2] != "__") and v not in [str, int, datetime, bool,
                                                                     float] and inspect.isclass(v):
                re_modify = __wrap_pydantic__(cls.__name__, v, False)
                cls.__annotations__[k] = re_modify
                setattr(sys.modules[cls.__module__], k, re_modify)

        for k, v in cls.__annotations__.items():
            if not isinstance(v,str) and ( v.__module__ == typing.__name__):
                temp = []
                for fv in v.__args__:

                    if check_is_need_pydantic(fv):
                        if get_cls(fv) is None:
                            re_modify = __wrap_pydantic__(cls.__name__, fv, False)
                            # setattr(sys.modules[fv.__module__],fv.__name__,re_modify)
                            # setattr(sys.modules[__cls__.__module__], fv.__name__, re_modify)

                            temp += [re_modify]
                        else:
                            temp += [get_cls(fv)]
                    else:
                        temp += [fv]
                # v.__args__ =tuple(temp)
                cls.__annotations__[k].__args__ = tuple(temp)




            elif v not in [str, int, datetime, bool, float] and inspect.isclass(v):
                if cls.__annotations__.get(k) is not None:
                    if get_cls(cls) is None:
                        re_modify = __wrap_pydantic__(cls.__name__, v, False)
                        cls.__annotations__[k] = re_modify
                        setattr(sys.modules[re_modify.__module__], k, re_modify)
    ret_cls = None
    try:
        ret_cls = type(f"{cls.__name__}", (cls, pydantic.BaseModel,), dict(cls.__dict__))
    except pydantic.errors.PydanticUserError as ex:
        ret_cls = type(f"{cls.__name__}", (cls, pydantic.BaseModel,), {})
        # ret_cls.__annotations__ = cls.__dict__['model_fields']


    def get_mdl(cls):
        if sys.modules.get(cls.__module__):
            return sys.modules[cls.__module__]
        else:
            for k, v in sys.modules.items():
                if hasattr(v, "__file__"):
                    if v.__file__ == cls.__module__:
                        return v

    cls_module = get_mdl(cls)
    setattr(cls_module, cls.__name__, ret_cls)
    ret_cls.__name__ = cls.__name__
    __wrap_pydantic_cache__[f"{cls.__module__}/{cls.__name__}"] = ret_cls
    return __wrap_pydantic_cache__.get(f"{cls.__module__}/{cls.__name__}")


def check_is_need_pydantic(cls):
    if isinstance(cls,typing.ForwardRef):
        return check_is_need_pydantic(cls.__forward_arg__)
    if isinstance(cls,str):
        return False

    if inspect.isclass(cls):
        if cls.__module__ == bytes.__module__ and cls.__name__ == "NoneType":
            return False

    if isinstance(cls, tuple):
        ret = False
        for x in cls:
            ret = ret or check_is_need_pydantic(x)
        return ret
    if cls.__module__ == typing.__name__ and cls.__origin__ == list and hasattr(cls, "__args__"):
        return check_is_need_pydantic(cls.__args__)
    if inspect.isclass(cls) and (cls == fastapi.Request or issubclass(cls, fastapi.Request)):
        return False
    if not inspect.isclass(cls) and callable(cls):
        return False
    if hasattr(cls, "__origin__") and cls.__origin__ == List.__origin__ and hasattr(cls,
                                                                                    "__args__") and isinstance(
        cls.__args__, tuple):
        ret = []
        for x in cls.__args__:
            if check_is_need_pydantic(x):
                ret += [__wrap_pydantic__("", x, is_lock=False)]
            else:
                ret += [x]
        cls.__args__ = tuple(ret)

        return False

    ret = (cls not in [str, int, float, datetime, bool, dict, bytes]) and (
            inspect.isclass(cls) and (not issubclass(cls, pydantic.BaseModel)))
    return ret


class RequestHandler:

    def __init__(self, method, path, handler):
        if method == "get":
            self.path = path
            self.method = method
            self.handler = handler
            self.return_type = None
            return

        self.path = path
        __old_dfs__ = []
        self.return_type = None
        tmp_lst = []
        if handler.__defaults__ is not None:
            pos = 0
            tmp_lst = list(handler.__defaults__)
            for x in handler.__defaults__:

                if type(x) == fastapi.params.File:
                    method = "form"

                if inspect.isclass(x) and issubclass(x, fastapi.UploadFile):
                    tmp_lst[pos] = fastapi.File()
                    method = "form"

                pos += 1

            handler.__defaults__ = tuple(tmp_lst)

            __old_dfs__ = list(handler.__defaults__)
        __annotations__: dict = handler.__annotations__
        __defaults__ = []
        tmp_lst = []
        for k, v in __annotations__.items():
            if hasattr(v, "__module__") and v.__module__ == "typing" and hasattr(v,
                                                                                 "__origin__") and v.__origin__ == list and hasattr(
                v, "__args__") and isinstance(v.__args__, tuple):
                arg_type = v.__args__[0]
                if inspect.isclass(arg_type) and issubclass(arg_type, fastapi.UploadFile):
                    method = "form"
                    tmp_lst += [fastapi.File()]
            if inspect.isclass(v) and issubclass(v, fastapi.UploadFile):
                method = "form"
                tmp_lst += [fastapi.File()]

        if method == "form":
            if handler.__defaults__ is not None:
                handler.__defaults__ = tuple(tmp_lst + list(handler.__defaults__))
            else:
                handler.__defaults__ = tuple(tmp_lst)

        for k, v in __annotations__.items():

            if method != "form":

                if hasattr(v, "__module__") and v.__module__ == "typing" and v.__str__().startswith(
                        "typing.Union[") and v.__str__().endswith("NoneType]"):
                    __defaults__ += [fastapi.Body(
                        default=None,
                        embed=True,
                        title=k
                    )]
                if hasattr(v, "__module__") and v.__module__ == "typing" and v.__str__().startswith(
                        "typing.Optional["):
                    __defaults__ += [fastapi.Body(
                        default=None,
                        embed=True,
                        title=k
                    )]
                    # handler.__annotations__[k]=v.__args__[0]


                elif v == fastapi.Request:
                    continue
                if check_is_need_pydantic(v):
                    handler.__annotations__[k] = __wrap_pydantic__("", v)
                    if k != "return":
                        __defaults__ += [fastapi.Body(title=k, embed=True)]

                    else:
                        self.return_type = handler.__annotations__[k]
                        __defaults__ += [fastapi.Body(embed=True)]
                elif (not (hasattr(v, "__module__") and v.__module__ == "typing")) and v not in [str, int, bool,
                                                                                                 datetime,
                                                                                                 float] and issubclass(
                    v, pydantic.BaseModel) and k != "return":
                    __defaults__ += [fastapi.Body(embed=True)]
                elif v in [str, int, bool, datetime, float] and k != "return" and f"{k}" not in path:
                    __defaults__ += [fastapi.Body(embed=True)]

            else:

                if k == "return":
                    if check_is_need_pydantic(v):
                        handler.__annotations__[k] = __wrap_pydantic__("", v)
                elif "{" + k + "}" in self.path:
                    continue
                elif k != "return" and v in [str, int, float, bool, datetime]:
                    __defaults__ += [fastapi.Form(...)]
                    __annotations__[k] = Union[v, None]
                elif v == fastapi.UploadFile or v == fastapi.Request or \
                        (hasattr(v, "__origin__") and v.__origin__ == List[fastapi.UploadFile].__origin__
                         and hasattr(v, "__args__") and v.__args__[0] == fastapi.UploadFile):
                    continue
                # if not "{" + k + "}" in self.path:
                #     import typing

                # elif k != "return" :
                #     continue
                elif k != "return":
                    __defaults__ += [fastapi.Form(...)]
                    # __wrap_pydantic__(handler.__name__, v)

        # def new_handler(*args,**kwargs):
        #     handler(*args,**kwargs)
        if method != "form":
            __defaults__ += __old_dfs__
            handler.__defaults__ = tuple(__defaults__)
        else:
            handler.__defaults__ = tuple(__defaults__ + list(handler.__defaults__))
        self.handler = handler
        if method == "form": method = "post"
        self.method = method


def __wrapper_class__(method: str, obj, path: str):
    pass


def __wrapper_func__(method: str, obj, path) -> RequestHandler:
    fx = RequestHandler(method, path, obj)
    return fx


from fastapi import FastAPI, Request

from typing import Optional, Dict
from fastapi.security.oauth2 import OAuth2PasswordBearer
import fastapi.params
import os
from fastapi.templating import Jinja2Templates
import importlib.util
from importlib import machinery
import sys

# wellknown_app: FastAPI = None
# __instance__ = None


class BaseWebApp:
    def __init__(self):
        self.application_name = None
        self.main_module = None
        self.bind_ip = None
        self.bind_port = None
        self.host_url = None
        self.host_api_url = None
        self.host_schema = None
        self.__routers__ = None
        self.app: FastAPI = None
        self.controller_dirs: List[str] = []
        self.logs_dir: str = None
        self.logs: logging.Logger = None
        self.working_dir: str = None
        self.host_dir: str = None
        self.dev_mode: bool = False
        self.api_host_dir = "api"
        self.static_dir: str = None
        self.template_dir: str = None
        self.templates: Jinja2Templates = None
        self.url_get_token: str = None

        self.jwt_algorithm = "HS256"
        self.jwt_secret_key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
        self.oauth2_type = None
        self.__on_auth__ = None
        self.request_handlers = dict()
        self.on_auth_user = None

    def load_controller_from_dir(self, route_prefix: str = None, controller_dir: str = None):
        if controller_dir == None:
            return
        if controller_dir[0:2] == "./":
            controller_dir = os.path.join(self.working_dir, controller_dir[2:])
        controller_dir = controller_dir.replace('/', os.sep)
        if not os.path.isdir(controller_dir):
            print(f"{controller_dir} was not found")
            # self.logs.error(msg=f"{controller_dir} was not found")
            raise (f"{controller_dir} was not found")
            return
        root_dir, dirs, files = list(os.walk(controller_dir))[0]

        sys.path.append(self.working_dir)
        sys.path.append(root_dir)
        for x in dirs:
            sys.path.append(x)
        so_files = [x for x in files if os.path.splitext(x)[1]=='.so']
        so_files_name = [x.split('.')[0] for x in files if os.path.splitext(x)[1] == '.so']
        py_files = [x.split('.')[0] for x in files if os.path.splitext(x)[1] == '.py']

        for _file_ in py_files:
            # if _file_ not in so_files_name:
            self.load_controller_from_file(os.path.join(root_dir,f"{_file_}.py"), route_prefix)
        for _file_ in so_files:
            self.load_controller_from_file(os.path.join(root_dir, _file_), route_prefix)
        for dir in dirs:
            self.load_controller_module_dir(os.path.join(root_dir, dir), route_prefix)

    def create_logs(self, logs_dir) -> logging.Logger:
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)

        _logs = logging.Logger("web")
        hdlr = logging.FileHandler(logs_dir + '/log{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S_%f')))
        _logs.addHandler(hdlr)
        return _logs

    def load_controller_module_dir(self, module_dir, prefix: str = None) -> List[object]:

        # import pyx_re_quicky_routers
        module_path = os.path.join(module_dir, "__init__.py")
        _, _, files = list(os.walk(module_dir))[0]
        for _file_ in files:
            if os.path.splitext(_file_)[1] == ".py":
                full_file_path = os.path.join(module_dir, _file_)
                if os.path.isfile(full_file_path):
                    self.load_controller_from_file(full_file_path, prefix)

    def auth(self):
        def wrapper(fn):
            setattr(self.oauth2_type, "__call__", fn)

        return wrapper

    def load_controller_from_file(self, full_file_path, prefix):
        if os.path.splitext(full_file_path)[1] not in ['.py','.so']:
            return
        if not os.path.isfile(full_file_path):
            return
        if os.path.splitext(full_file_path).__len__() != 2 and os.path.splitext(full_file_path)[1] != ".py":
            return

        src = machinery.SourceFileLoader(full_file_path, full_file_path)

        spec = importlib.util.spec_from_loader(full_file_path, src)
        _mdl_ = None
        if os.path.splitext(full_file_path)[1] == '.py':
            _mdl_ = importlib.util.module_from_spec(spec)
        elif os.path.splitext(full_file_path)[1] == '.so':
            _mdl_ = importlib.util.module_from_spec(spec)

        sys.modules[_mdl_.__name__] = _mdl_
        if hasattr(sys.modules[_mdl_.__name__], "__cy_web_has_load_controller__"):
            return
        __cy_web_has_load_controller__ = False
        if os.path.splitext(full_file_path)[1] == '.py':
            spec.loader.exec_module(_mdl_)
        for k, v in _mdl_.__dict__.items():
            if isinstance(v, RequestHandler):

                __cy_web_has_load_controller__ = True
                _path = "/" + v.path
                if prefix is not None and prefix != "":
                    _path = "/" + prefix + _path
                if self.host_dir is not None:
                    _path = self.host_dir + _path
                if v.return_type is None:
                    if hasattr(v.handler, "__annotations__"):
                        if v.handler.__annotations__.get("return") is not None:
                            v.return_type = v.handler.__annotations__.get("return")

                if v.return_type is not None:
                    try:
                        getattr(self.app, v.method)(_path, response_model=v.return_type)(v.handler)
                    except Exception as e:
                        raise Exception(f"Error when create handler\n"
                                        f"Please preview file {v.handler.__code__.co_filename}\n"
                                        f"Error msg\n"
                                        f"\t{e}")
                else:
                    while "//" in _path:
                        _path = _path.replace("//","/")
                    getattr(self.app, v.method)(_path)(v.handler)
                self.request_handlers[v.path] = v
        if __cy_web_has_load_controller__:
            setattr(sys.modules[_mdl_.__name__], "__cy_web_has_load_controller__", True)


__cache_apps__ = {}
__cache_apps_lock__ = threading.Lock()
__instance__ = None
web_application = None
from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from typing import Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from  fastapi.responses import JSONResponse

def create_access_token(data: dict, expires_delta=None, SECRET_KEY=None, ALGORITHM=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": None})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def login_for_access_token(request: fastapi.Request, form_data: OAuth2PasswordRequestForm = Depends()):
    global web_application
    if not isinstance(web_application, WebApp):
        raise Exception("WebApp was not found")
    if web_application.on_auth_user is None:
        raise Exception("Please create on auth user with  cy_web_x.auth_user")
    user = web_application.on_auth_user(request, form_data.username, form_data.password)
    if not isinstance(user, dict):
        raise Exception(
            f"{web_application.on_auth_user.__name__} in {web_application.on_auth_user.__code__.co_filename} must return dictionary with username:str and application:str,is_ok:bool")
    if set(["username", "application", "is_ok"]).intersection(list(user.keys())) != set(
            ["username", "application", "is_ok"]):
        raise Exception(
            f"{web_application.on_auth_user.__name__} in {web_application.on_auth_user.__code__.co_filename} must return dictionary with username:str and application:str,is_ok:bool")
    if user.get("is_ok") == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {
            "username": user.get("username"),
            "application": user.get("application")
        }, expires_delta=None,
        SECRET_KEY=web_application.jwt_secret_key,
        ALGORITHM=web_application.jwt_algorithm
    )
    ret = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    ret.set_cookie("cy-files-token",access_token)
    return ret


class WebApp(BaseWebApp):

    def __init__(self,

                 working_dir: str,
                 bind: str = "0.0.0.0:8011",
                 host_url: str = "http://localhost:8011",
                 logs_dir: str = "./logs",
                 controller_dirs: List[str] = [],
                 api_host_dir: str = "api",
                 static_dir: str = None,
                 dev_mode: bool = False,
                 template_dir: str = None,
                 url_get_token: str = "api/accounts/token",
                 jwt_algorithm: str = "HS256",
                 jwt_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
                 cache_folder: str = "./cache"
                 ):
        global __cache_apps__
        global __cache_apps_lock__
        global web_application
        web_application = self
        self.request_handlers = dict()

        if sys.platform == "win32":
            self.app.middleware("http")(windows_fxi_javascript_resource)
        self.url_get_token = url_get_token
        self.jwt_algorithm = jwt_algorithm
        self.jwt_secret_key = jwt_secret_key
        self.template_dir = template_dir
        self.dev_mode = dev_mode
        self.api_host_dir = api_host_dir

        self.working_dir = working_dir
        if cache_folder[0:2] == "./":
            cache_folder = os.path.join(self.working_dir, cache_folder[2:])
            if not os.path.isdir(cache_folder):
                os.makedirs(cache_folder, exist_ok=True)
        self.cache_folder = cache_folder
        self.static_dir = static_dir
        if self.static_dir is not None and self.static_dir[0:2] == "./":
            self.static_dir = os.path.join(self.working_dir, self.static_dir[2:])
        self.logs_dir = logs_dir
        if self.logs_dir[0:2] == "./":
            self.logs_dir = os.path.join(self.working_dir, self.logs_dir[2:])
        self.logs: logging.Logger = self.create_logs(self.logs_dir)
        if len(bind.split(":")) < 2:
            raise Exception(f"bind in {self.__module__}.{WebApp.__name__}.__init__ must look like 0.0.0.0:1234")
        self.bind_ip = bind.split(':')[0]
        self.bind_port = int(bind.split(':')[1])
        self.host_url = host_url
        self.host_schema = self.host_url.split(f"://")[0]
        remain = self.host_url[self.host_schema.__len__() + 3:]
        self.host_name = remain.split('/')[0].split(':')[0]
        self.host_port = None
        self.host_api_url = self.host_url + "/" + self.api_host_dir
        if remain.split('/')[0].split(':').__len__() == 2:
            self.host_port = int(remain.split('/')[0].split(':')[1])
            remain = remain[self.host_name.__len__() + str(self.host_port).__len__() + 1:]
        else:
            remain = remain[self.host_name.__len__() + 1:]


        self.host_dir = None
        if remain != "":
            self.host_dir = remain
        if self.host_dir and not self.host_dir.startswith('/'):
            self.host_dir= '/'+ self.host_dir
        while self.host_dir  and "//" in self.host_dir:
            self.host_dir = self.host_dir.replace('//','/')
        if self.host_dir is not None:
            self.app = fastapi.FastAPI(
                docs_url=f"/{self.host_dir.lstrip('/').rstrip('/')}/docs",
                openapi_url=f"/{self.host_dir.lstrip('/').rstrip('/')}/docs/openapi.json"
            )
        else:
            self.app = fastapi.FastAPI()
        if self.static_dir is not None:

            if self.host_dir is not None and self.host_dir != "":
                self.app.mount(self.host_dir + "/static", StaticFiles(directory=self.static_dir), name="static")
            else:
                self.app.mount("/static", StaticFiles(directory=self.static_dir),
                               name="static")
        if self.template_dir is not None and self.template_dir[0:2] == "./":
            self.template_dir = os.path.join(self.working_dir, self.template_dir[2:])
        if self.template_dir is not None:
            self.templates = Jinja2Templates(directory=self.template_dir)

        self.controller_dirs = []
        for x in controller_dirs:
            if x[0:2] == "./":
                self.controller_dirs += [
                    os.path.join(self.working_dir, x[2:])
                ]
            else:
                self.controller_dirs += [x]
        for x in self.controller_dirs:
            self.load_controller_from_dir(x)
        # if self.host_dir is not None and self.host_dir != "":
        #     self.url_get_token = self.host_dir + "/" + self.url_get_token
        self.url_get_token = self.url_get_token.lstrip('/')
        print(f"Login url {self.url_get_token}")
        self.app.post("/" + self.url_get_token)(login_for_access_token)

    def gunicorn_start(self, start_path):
        global web_application
        from gunicorn.app import wsgiapp
        wsgiapp.run()

    def unvicorn_start(self, start_path, worker=4):
        global web_application
        # for k,v in self.web_app_module.__dict__.items():
        #     if v==self:
        #        self.web_app_name=k
        if not isinstance(web_application, WebApp):
            raise Exception("Web application can not start")
        run_path = f"{start_path}:web_application.app"
        print(run_path)
        # if not self.dev_mode:
        #     run_path=web_application.app
        # if self.dev_mode:
        uvicorn.run(
            app=run_path,
            # loop="asyncio",
            host=self.bind_ip,
            port=self.bind_port,
            log_level="debug",
            # lifespan='on',
            # ws_max_size=8*8 * 1024*1024,
            reload=self.dev_mode,
            reload_dirs=self.working_dir,
            workers=worker,
            # ws='websockets',
            # backlog=1000,
            # interface='asgi3',
            # timeout_keep_alive=True,
            # h11_max_incomplete_event_size=1024 * 1024 * 8,
            # http="httptools",
        )
        # else:
        #     uvicorn.run(
        #         run_path,
        #         # loop="asyncio",
        #         host=self.bind_ip,
        #         port=self.host_port,
        #         log_level="info",
        #         lifespan='on',
        #         # ws_max_size=16777216 * 1024,
        #         # reload=self.dev_mode,
        #         reload_dirs=self.working_dir,
        #         workers=worker,
        #         # ws='websockets',
        #         backlog=1000,
        #         # interface='WSGI',
        #         timeout_keep_alive=True
        #
        #     )


def web_handler(path: str, method: str, response_model=None):
    def warpper(obj):
        import inspect
        if inspect.isclass(obj):
            return __wrapper_class__(method, obj, path)
        elif callable(obj):
            # fx= fastapi.FastAPI()
            # fx.get(response_model=)

            return __wrapper_func__(method, obj, path)

    return warpper


def add_controller(web_app, prefix_path: str, controller_dir):
    web_app.load_controller_from_dir(prefix_path, controller_dir)


async def windows_fxi_javascript_resource(request: Request, call_next):
    res = await call_next(request)
    if request.url.path.endswith('.js') and '/static/' in request.url.path:
        t, _ = mimetypes.guess_type(request.url.path)
        res.headers['content-type'] = t

    return res


def start_with_guicorn(worker):
    global web_application
    if isinstance(web_application, WebApp):
        web_application.gunicorn_start(
            f"{WebApp.__module__}",

        )
        print("web run on:")
        print(web_application.host_url)


def start_with_uvicorn(worker=4):
    global web_application
    if isinstance(web_application, WebApp):
        web_application.unvicorn_start(
            f"{WebApp.__module__}",
            worker
        )
        print("web run on:")
        print(web_application.host_url)
    # run_path=path.replace(os.sep,"/").replace('/','.')
    # web_app.unvicorn_start(run_path)


def start_with_gunicorn(worker=4):
    global web_application
    if isinstance(web_application, WebApp):
        web_application.unvicorn_start(
            f"{WebApp.__module__}",
            worker
        )
        print("web run on:")
        print(web_application.host_url)


def load_controller_from_dir(prefix, controller_path):
    global web_application
    if isinstance(web_application, WebApp):
        web_application.load_controller_from_dir(
            prefix, controller_path
        )


def middleware():
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.app.middleware("http")


def fast_api() -> fastapi.FastAPI:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.app


def add_cors(origins: List[str]):
    global web_application
    if isinstance(web_application, WebApp):
        web_application.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

from  starlette.requests import Request
def get_host_url(request:Request) -> str:
    global web_application
    if isinstance(web_application, WebApp):
        scheme = request.headers.get("x-forwarded-proto", request.base_url.components.scheme)
        netloc = request.base_url.components.netloc
        return f"{scheme}://{netloc}{get_host_dir()}"


def get_host_dir() -> str:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.host_dir


def get_working_dir() -> str:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.working_dir


def get_template_dir() -> str:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.template_dir


def get_template_dir() -> int:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.host_port


def get_bind_ip() -> str:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.bind_ip


def get_fastapi_app() -> FastAPI:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.app


def render_template(rel_path_to_template_page: str, render_data: dict):
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.templates.TemplateResponse(
            rel_path_to_template_page,
            render_data

        )


def get_static_dir():
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.static_dir


def get_token_url():
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.url_get_token


def get_jwt_secret_key():
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.jwt_secret_key


def get_jwt_algorithm():
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.jwt_algorithm


import starlette.requests


def validate_token_in_request(self, request):
    token = None
    if (hasattr(request,"cookies")
            and isinstance(request.cookies,dict) and
            request.cookies.get('access_token_cookie') is not None):
        token = request.cookies['access_token_cookie']
    elif (hasattr(request,"cookies") and
          isinstance(request.cookies,dict) and
          request.cookies.get('cy-files-token') is not None):
        token = request.cookies['cy-files-token']
    else:
        authorization: str = request.headers.get("Authorization")
        if authorization is None:
            raise fastapi.exceptions.HTTPException(status_code=401)
        scheme, token = tuple(authorization.split(' '))
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
    try:

        ret_data = jwt.decode(token, self.jwt_secret_key,
                              algorithms=[self.jwt_algorithm],
                              options={"verify_signature": True},
                              )
        username = ret_data.get("username", ret_data.get("sub"))
        application = ret_data.get("application")
        if username is None or application is None:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        setattr(request, "username", username)
        setattr(request, "application", application)
        if self.validate(request, username, application):
            return dict(token=token, username=username, application=application)
        else:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jose.exceptions.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jose.exceptions.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


def auth_type(a_type: type):
    def default_init(ins):
        global web_application
        assert isinstance(web_application, WebApp)
        a_type.__init__(ins, web_application.url_get_token)

    def wrapper(cls):
        global web_application
        assert isinstance(web_application, WebApp)
        cls = type(f"{cls.__name__}", (cls, a_type), {})
        if not hasattr(cls, "validate"):
            raise Exception(f"{cls.__module__}.{cls.__name__} must have validate function looks like:\n"
                            f"def validate(self,request:fastapi.Request,username:str,application:str)->bool:\n"
                            f" blab ...")
        validate = getattr(cls, "validate")
        setattr(cls, "__init__", default_init)
        validate_token_in_request.__annotations__["request"] = validate.__annotations__["request"]
        setattr(cls, "__call__", validate_token_in_request)
        instance = cls()
        setattr(instance, "jwt_secret_key", web_application.jwt_secret_key)
        setattr(instance, "jwt_algorithm", web_application.jwt_algorithm)

        def on_auth_user(request, username, password):
            return instance.validate_account(request, username, password)


        web_application.on_auth_user = on_auth_user
        return instance

    return wrapper


import pydantic.fields


def model(all_fields_are_optional: bool = False):
    def warpper(cls):
        for x in cls.__bases__:
            if hasattr(x, "__annotations__"):
                for k, v in x.__annotations__.items():
                    if all_fields_are_optional:
                        cls.__annotations__[k] = Optional[v]
                    else:
                        cls.__annotations__[k] = v
        for k, v in cls.__annotations__.items():
            if isinstance(v, tuple):
                v_t = v[0]
                v_d = ""
                v_r = False
                for x in v:
                    if isinstance(x, type):
                        v_t = x
                    if isinstance(x, str):
                        v_d = x
                    if isinstance(x, bool):
                        v_r = x
                cls.__annotations__[k] = v_t

                setattr(cls, k, pydantic.Field(
                    description=v_d,
                ))
            else:
                if all_fields_are_optional:
                    cls.__annotations__[k] = Optional[v]

        return __wrap_pydantic__("", cls, False)

    return warpper


def get_cache_folder_path() -> str:
    global web_application
    if isinstance(web_application, WebApp):
        return web_application.cache_folder


__cache_content_dict__ = {}
__cache_content_dict_lock__ = threading.Lock()


def cache_content(relative_folder: str, file_name, content: bytes) ->typing.Optional[str]:
    global web_application
    global __cache_content_dict__
    if isinstance(web_application, WebApp):
        key = f"{relative_folder}/{file_name}".lower()
        # cache_file_name = os.path.splitext(file_name)[1]
        # file_name_id = file_name.split('_')[0]
        # file_name = f"{file_name_id}.{cache_file_name}"



        if not __cache_content_dict__.get(key):

            file_cache = os.path.join(web_application.cache_folder, relative_folder.replace('/', os.sep))
            if not os.path.isdir(file_cache):
                os.makedirs(file_cache, exist_ok=True)
            file_cache = os.path.join(file_cache, file_name)
            if not os.path.isfile(file_cache):
                if isinstance(content,bytes):
                    with open(file_cache, "wb") as f:
                        f.write(content)
                else:
                    return  None

            __cache_content_dict__[key] = file_cache

    return __cache_content_dict__[key]


def cache_content_check(relative_folder: str, file_name):
    global web_application
    global __cache_content_dict__
    if isinstance(web_application, WebApp):
        key = f"{relative_folder}/{file_name}".lower()

        if not __cache_content_dict__.get(key):
            file_cache = os.path.join(web_application.cache_folder, relative_folder.replace('/', os.sep))
            if not os.path.isdir(file_cache):
                os.makedirs(file_cache, exist_ok=True)
            file_cache = os.path.join(file_cache, file_name)
            if not os.path.isfile(file_cache):
                return None
            __cache_content_dict__[key] = file_cache
    return __cache_content_dict__[key]


from fastapi import HTTPException, Request, status
from fastapi.responses import StreamingResponse, FileResponse
import mimetypes


def __get_range_header__(range_header: str, file_size):
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
        # if end ==1:
        #     end = file_size-1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()

    return start, end


import queue


def __send_bytes_range_requests__(
        file_obj, start: int, end: int, chunk_size: int = 10_000
):
    """Send a file in chunks using Range Requests specification RFC7233

        `start` and `end` parameters are inclusive due to specification
        """
    if hasattr(file_obj, "read_chunks") and callable(file_obj.read_chunks):
        ret = file_obj.read_chunks(start, end)
        for x in ret:
            yield x
    else:
        file_obj.seek(start)
        data = [1]
        pos = file_obj.tell()
        while len(data) > 0:
            read_size = min(chunk_size, end + 1 - pos)
            data = file_obj.read(read_size)

            yield data

import inspect
async def __send_bytes_range_requests_async__(
        file_obj, start: int, end: int, chunk_size: int = 10_000
):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    file_obj.seek(start)
    data = [1]
    pos = file_obj.tell()
    while len(data) > 0:
        read_size = min(chunk_size, end + 1 - pos)
        if inspect.iscoroutinefunction(file_obj.read):
            data = await file_obj.read(read_size)
        else:
            data = file_obj.read(read_size)
        yield data
    file_obj.close()


from functools import partial
import anyio
import os
import stat
import sys
import typing
from starlette.types import Receive, Send, Scope
from fastapi import Response
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool

Content = typing.Union[str, bytes]
SyncContentStream = typing.Iterator[Content]
AsyncContentStream = typing.AsyncIterable[Content]
ContentStream = typing.Union[AsyncContentStream, SyncContentStream]


class AsyncStreamingResponse(Response):
    body_iterator: AsyncContentStream

    def __init__(
            self,
            file_Stream,
            start,
            end,
            segment_size,
            buffering_size,
            content: ContentStream,
            status_code: int = 200,
            headers: typing.Optional[typing.Mapping[str, str]] = None,
            media_type: typing.Optional[str] = None,
            background: typing.Optional[BackgroundTask] = None,
    ) -> None:

        self.start = start
        self.end = end
        size = self.end - self.start
        self.segment_size = segment_size
        self.buffering_size = buffering_size

        self.file_Stream = file_Stream
        self.content_reader = content
        self.status_code = status_code
        self.media_type = self.media_type if media_type is None else media_type
        self.background = background
        x = self.start
        y = min(self.end, self.start + self.segment_size - 1)
        headers[
            'content-range'] = f"bytes {x}-{y}/{self.file_Stream.get_size()}"
        self.init_headers(headers)

    async def listen_for_disconnect(self, receive: Receive) -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                self.file_Stream.close()

                break

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        self.file_Stream.seek(self.start)
        data = [1]
        pos = self.file_Stream.tell()
        b_size = 0
        while len(data) > 0:
            read_size = min(self.buffering_size, self.end + 1 - pos)
            data = self.file_Stream.read(read_size)
            if data.__len__() > 0:
                await send({"type": "http.response.body", "body": data, "more_body": True})
            else:
                await send({"type": "http.response.body", "body": data, "more_body": True})
                break
            b_size += read_size

        # self.file_Stream.seek(self.start)

        # begin = self.file_Stream.tell()
        #
        # while begin<self.end:
        #     data = self.file_Stream.read(min(self.buffering_size, self.end - begin))
        #     await send({"type": "http.response.body", "body": data, "more_body": True})
        #     begin = self.file_Stream.tell()
        #     # end = min(self.end, begin + self.segment_size)
        #     # while begin <end:
        #     #
        #     #     end = begin+data.__len__()

        # await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async with anyio.create_task_group() as task_group:
            async def wrap(func: "typing.Callable[[], typing.Awaitable[None]]") -> None:
                await func()
                task_group.cancel_scope.cancel()

            task_group.start_soon(wrap, partial(self.stream_response, send))
            await wrap(partial(self.listen_for_disconnect, receive))

        if self.background is not None:
            await self.background()


def __read_chunks_iter__(gfs, start: int, end: int):
    segment_len = gfs.cursor_len
    chunk_index, remain = divmod(start, gfs.chunk_size)
    segment_run =segment_len
    cursor = gfs.get_cursor(chunk_index, segment_run)
    size_read = 0

    total, m = divmod(end - start, gfs.chunk_size)
    if m > 0:
        total += 1
    while size_read < (end - start):
        try:
            t = datetime.utcnow()
            data = cursor.next()["data"]
            if size_read == 0 and remain > 0:
                data = data[remain:]

            if size_read + data.__len__() > end - start + 1:
                data = data[:end - size_read+1]
            size_read += data.__len__()
            yield data

        except StopIteration as e:
            chunk_index += segment_run
            segment_run = segment_len
            cursor.close()

            cursor = gfs.get_cursor(chunk_index, segment_run)
    cursor.close()


async def streaming_async(fsg, request, content_type, streaming_buffering=1024 * 8 * 8, segment_size=None):
    """
    Streaming content
    :param fsg: mongodb gridOut
    :param request: __client__ request
    :param content_type: mime_type
    :param streaming_buffering: support 4k
    :return:
    """
    file_size = fsg.get_size()

    range_header = request.headers.get("range")
    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        # "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, "
            "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1

    status_code = 200

    if range_header is not None:
        start, end = __get_range_header__(range_header, file_size)
        size = end - start + 1

        # end = start+size-1

        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT
    if segment_size:
        res = AsyncStreamingResponse(
            file_Stream=fsg,
            start=start,
            end=end,
            segment_size=segment_size,
            buffering_size=streaming_buffering,
            content=None,
            headers=headers,
            status_code=status_code,
            media_type=content_type
        )

    else:
        if hasattr(fsg, "delegate"):
            # if hasattr(fsg,"__init_delegate__") and callable(fsg.__init_delegate__):
            #     fsg.__init_delegate__()
            #     content = __send_bytes_range_requests_async__(fsg.delegate, start, end, streaming_buffering)
            # else:
            content = __send_bytes_range_requests_async__(fsg, start, end, streaming_buffering)
        elif hasattr(fsg, "__delegate__"):
            content = __send_bytes_range_requests_async__(fsg, start, end, streaming_buffering)
        elif hasattr(fsg, "get_cursor") and callable(fsg.get_cursor):
            content = __read_chunks_iter__(fsg, start, end)
        else:
            content = __send_bytes_range_requests__(fsg, start, end, streaming_buffering)

        res = StreamingResponse(
            content=content,
            media_type=content_type,
            status_code=status_code,
            headers=headers
        )
    if content_type.startswith("video/") or content_type.startswith("audio/"):
        return res
    res.headers.append("Cache-Control", "max-age=86400")
    res.headers.append("Content-Type", content_type)

    return res
