import pathlib
import os
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
import cyx.video.extract_text_from_video_service

sv = cy_kit.singleton(
    cyx.video.extract_text_from_video_service.ExtractTextFromVideoService
)
src_file = f"/home/vmadmin/python/v6/file-service-02/dataset/test.mp4"
fx= sv.get_all_text(
    source_path=src_file
)

print(fx.__len__())