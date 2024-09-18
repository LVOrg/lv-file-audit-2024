import math

import cy_kit
from PIL import Image
import os
import img2pdf


class GraphicsService:
    def scale(self, source: str, dest: str, size, skip_if_exist: bool = True):
        # thumb_dir = os.path.join(temp_thumb, app_name)
        if os.path.isfile(dest) and skip_if_exist:
            return dest
        image = Image.open(source)
        h, w = image.size
        nh, nw = int(size), int(size)
        if h > w:
            rate = float(size / h)
            nh = int(math.ceil(h * rate))
        elif w > h:
            rate = float(size / w)
            nw = int(math.ceil(w * rate))

        image.thumbnail((nh, nw))
        image.save(dest)
        image.close()
        del image
        return dest

    def convert_to_pdf(self, source: str, dest: str, skip_if_exist: bool = True):
        if os.path.isfile(dest) and skip_if_exist:
            return dest
        # image = Image.open(source)
        pdf_bytes = img2pdf.convert(source)
        with open(dest, "wb") as file:
            file.write(pdf_bytes)
            file.close()
        del pdf_bytes
        return dest
