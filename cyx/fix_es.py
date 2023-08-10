from pytz import unicode

import cy_kit
import cy_es
from cy_xdoc.services.search_engine import SearchEngine
se:SearchEngine = cy_kit.singleton(SearchEngine)
import re
import unicodedata


def no_accent_vietnamese(s):
    s = s.decode('utf-8')
    s = re.sub(u'Đ', 'D', s)
    s = re.sub(u'đ', 'd', s)
    return unicodedata.normalize('NFKD', unicode(s)).encode('ASCII', 'ignore')
index= "lv-codx_lv-docs"
items = cy_es.get_docs(
    client=se.client,
    index= index)

for x in items:
    cy_es.delete_doc(
        client=se.client,
        index=index,
        id= x.id
    )
    print(x)