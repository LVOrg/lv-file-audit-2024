import cy_kit
from cyx.rdr_segmenter.segmenter_services import VnSegmenterService
svc= cy_kit.singleton(VnSegmenterService)
print(svc.parse_word_segment("dasd dasdasd "))
