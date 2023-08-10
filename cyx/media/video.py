import os
import pathlib
import sys
from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfMerger
import cy_kit


from cyx.common.share_storage import ShareStorageService
class VideoServices:
    def __init__(self,share_storage_service:ShareStorageService = cy_kit.singleton(ShareStorageService)):
        self.share_storage_service = share_storage_service
        self.working_folder = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.processing_folder = self.share_storage_service.get_temp_dir(VideoServices)
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)

    def get_pdf(self, file_path: str, num_of_segment=100):
        import cyx.media.image_extractor
        image_extractor_service = cy_kit.singleton(cyx.media.image_extractor.ImageExtractorService)
        clip = VideoFileClip(
            file_path
        )
        duration = clip.duration
        segment, _ = divmod(clip.duration,num_of_segment)
        segment = max(segment,15)
        second = 0
        image_file_name_only = pathlib.Path(file_path).stem
        ret_file = os.path.join(self.processing_folder, f"{image_file_name_only}.pdf")
        merger = PdfMerger()


        while second<duration:
            sub_clip = clip.subclip(second, second)
            frame = sub_clip.get_frame(0)
            height, width, _ = frame.shape

            img = Image.fromarray(frame, 'RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            # bytes_of_image = io.BytesIO(img_byte_arr)

            image_file = os.path.join(self.processing_folder, f"{image_file_name_only}_{second}.png")
            with open(image_file, 'wb') as f:  ## Excel File
                f.write(img_byte_arr)
            pdf_file = image_extractor_service.convert_to_pdf(image_file,file_ext="pdf")

            del img_byte_arr
            img.close()
            sub_clip.close()
            del img
            del sub_clip
            os.remove(image_file)
            merger.append(pdf_file)
            os.remove(pdf_file)
            second = min(second+segment,duration)
            cy_kit.clean_up()

        merger.write(ret_file)
        del merger
        cy_kit.clean_up()
        return ret_file

    def get_audio(self, file_path):
        clip = VideoFileClip(
            file_path
        )
        audio_file_name_only = pathlib.Path(file_path).stem
        ret_file = os.path.join(self.processing_folder, f"{audio_file_name_only}.wav")
        clip.audio.write_audiofile(ret_file)
        return ret_file

    def get_image(self, file_path, duration=None):
        clip = VideoFileClip(
            file_path
        )
        second, _ = divmod(clip.duration, 2)
        clip = clip.subclip(second, second)
        frame = clip.get_frame(0)
        height, width, _ = frame.shape

        img = Image.fromarray(frame, 'RGB')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        # bytes_of_image = io.BytesIO(img_byte_arr)

        image_file_name_only = pathlib.Path(file_path).stem

        ret_file = os.path.join(self.processing_folder, f"{image_file_name_only}.png")
        with open(ret_file, 'wb') as f:  ## Excel File
            f.write(img_byte_arr)
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
                return ret_file
        return ret_file
