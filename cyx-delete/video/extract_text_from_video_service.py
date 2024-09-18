import datetime
import typing

import cy_kit
import cyx.common.temp_file
import os
import pathlib
import sys
from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io
from cyx.easy_ocr import EasyOCRService
import cyx.graphic_utils as g_u


class FrameInfo:
    frame: int
    full_file_path: str
    content: str


class MediaInfo:
    fps: int
    frames: int
    duration: int


class TextFrame:
    duration_from: int
    duration_to: int
    content: str
    process_on: datetime.datetime
    time_process_in_m_second: int
    ord: int


class ExtractTextFromVideoService:
    def __init__(self,
                 tmp_file: cyx.common.temp_file.TempFiles = cy_kit.singleton(cyx.common.temp_file.TempFiles),
                 easy_ocr_service=cy_kit.singleton(EasyOCRService),
                 ):
        self.easy_ocr_service = easy_ocr_service
        self.tmp_file = tmp_file
        self.processing_folder = os.path.abspath(
            os.path.join(
                tmp_file.get_root_dir(),
                "tmp_video"
            )
        )
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)

    def get_info(self, source_path: str) -> MediaInfo:
        ret = MediaInfo()
        clip = VideoFileClip(
            source_path
        )
        ret.frames = int(clip.fps * clip.duration)
        ret.fps = clip.fps
        ret.duration = clip.duration
        clip.close()
        del clip
        if sys.platform == "linux":
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except Exception as e:
                pass
        return ret

    def get_frame(self, source_path: str, frame: int) -> FrameInfo:
        ret = FrameInfo()
        clip = VideoFileClip(
            source_path
        )
        frames = int(clip.fps * clip.duration)
        if frame < 0 or frame > frames:
            clip_duration = clip.duration
            clip.close()
            del clip
            if sys.platform == "linux":
                try:
                    import ctypes
                    libc = ctypes.CDLL("libc.so.6")
                    libc.malloc_trim(0)
                except Exception as e:
                    pass
            raise Exception(f"{frame} must be range in [0- {frames}]")

        __frame__ = clip.get_frame(frame/clip.fps)

        height, width, _ = __frame__.shape

        img = Image.fromarray(__frame__, 'RGB')
        img_byte_arr = io.BytesIO()

        # img_byte_arr = img_byte_arr.getvalue()
        # bytes_of_image = io.BytesIO(img_byte_arr)

        image_file_name_only = pathlib.Path(source_path).stem

        ret_file = os.path.join(self.processing_folder, f"{image_file_name_only}_{frame}_.png")
        gray_scale_path = os.path.join(self.processing_folder, f"{image_file_name_only}_gray_{frame}_.png")
        img.save(ret_file, format='PNG')
        n_img = g_u.load_from_file_as_numpy_array(ret_file)
        g_img = g_u.gray_scale(n_img)

        # i_img = g_u.enhance_contrast(n_img, g_img)
        g_u.save_use_cv2(g_img, gray_scale_path)
        # g_u.save_use_cv2(g_img, gray_scale_path)
        del n_img
        del g_img
        # del i_img
        os.remove(ret_file)
        ret.full_file_path = gray_scale_path
        ret.frame = frame
        del img_byte_arr
        img.close()
        clip.close()
        del img
        del clip
        if sys.platform == "linux":
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except Exception as e:
                return ret
        return ret

    def get_text(self, frame_info: FrameInfo) -> FrameInfo:
        frame_info.content = self.easy_ocr_service.get_text(frame_info.full_file_path)
        return frame_info

    def get_all_text_at(self, source_path: str, frame_no: int) -> FrameInfo:
        frm = self.get_frame(source_path, frame_no)
        return self.get_text(frm)

    def get_all_text(self, source_path: str) -> typing.List[TextFrame]:
        ret = []
        info = self.get_info(source_path)
        start_time =datetime.datetime.utcnow()
        i = 0
        info_text = self.get_all_text_at(
            source_path,
            frame_no=int(min(i, info.frames))
        )
        i+=info.fps
        while i<=info.frames:
            print(f"process at ={i}")
            new_info_text = self.get_all_text_at(
                source_path,
                frame_no=int(min(i,info.frames))
            )
            if new_info_text.content != info_text.content:
                txt_frame = TextFrame()
                txt_frame.duration_from = info_text.frame
                txt_frame.duration_to = new_info_text.frame - 1
                txt_frame.content = info_text.content
                txt_frame.process_on = start_time
                txt_frame.time_process_in_m_second = (datetime.datetime.utcnow() - start_time).total_seconds() * 1000
                ret += [
                    txt_frame
                ]
                info_text = new_info_text
                print(f"process in {txt_frame.time_process_in_m_second} ms")
                start_time = datetime.datetime.utcnow()
            i+=info.fps






        return ret