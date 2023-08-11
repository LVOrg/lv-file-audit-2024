import cy_kit
from cyx.rdr_segmenter.segmenter_services import VnSegmenterService

async def test(text:str,svc= cy_kit.singleton(VnSegmenterService)):
    ret = await svc.parse_word_segment_async(text)
    return ret