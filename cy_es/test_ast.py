import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import ast
import json
filter = "day(data_item.RegisterOn)=10 "
filter ="(content^1) search 'test'  and privileges['1'] like ['DEV']"
filter ="privileges['1'] like ['dev']"
filter = "(data_item.FileName^1) search 'Unknown'"
filter = "privileges['7'] like [0,'admin']"
filter = "(data_item.FileNameLower^10) search 'sample.pdf' or (content^5) search 'Đăng ký xe'"
filteres =[
    "day(data_item.RegisterOn)=10 ", # Loc the ngay
    "(content^1) search 'test'  and privileges['1'] like ['DEV']", #Search theo quyen
    "privileges['1'] like ['dev']",
    "(data_item.FileName^1) search 'Unknown'", # search theo fiela name
    "privileges['7'] like [0,'admin']", # search theo dac quyen
    "(data_item.FileNameLower^10) search 'sample.pdf' or (content^5) search 'Đăng ký xe'", # Seach voi 2 noi dung khac nhau tren 2 content khac nhau
    "data_item.FileNameLower like '*.pdf'",
    "Privileges['7'] like ['','admin']", # search theo dac quyen


]
filteres +=["not day(data_item.RegisterOn)=10 "]
filteres +=["(content^1,data_item.FileNameLower^100) search 'test' and privileges['7'] like ['']"]
filteres +=["privileges['7'] like ['']"]
filteres +=["(content^1,data_item.FileNameLower^100) search 'test'"]
filteres +=["((content^100, mata.content^1000)  search 'tai lieu codx') or (filename^10000 search 'docx xlsx pdf')"]
filteres +=["(content^100, mata.content^1000)  search 'tai lieu codx' or filename^10000 search 'docx xlsx pdf'"]
filteres +=["not day(data_item.RegisterOn)=10 "]
filteres +=["not data_item.FileName like '*.jpg*'"]
filteres +=["privileges['p'] like ['BGD-282023'] or privileges['7'] like ['']"]
filteres +=["privileges['u'] like ['E0007','Guest']"]

import cy_es



from cy_xdoc.services.search_engine import SearchEngine
import cy_kit
se = cy_kit.singleton(SearchEngine)
for filter in filteres:
    fx = cy_es.natural_logic_parse(filter) #Parse from natural logic to JSON
    vx = cy_es.create_filter_from_dict(fx) # Parse from JSON to real ElasticSearch Expression
    lst =se.full_text_search(
        app_name="default",
        page_size=400,
        page_index=0,
        logic_filter=fx,
        privileges=None,
        highlight=False,
        content=None
    )
    print(filter)
    print(fx)
    print(vx)
    print(lst.hits.total)

