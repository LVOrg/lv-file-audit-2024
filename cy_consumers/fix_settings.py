import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
se = cy_kit.singleton(SearchEngine)
se.update_settings(index="congtyqc", key="index.highlight.max_analyzed_offset",value="999999999")

