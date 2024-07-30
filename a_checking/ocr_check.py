import typing

from PyPDF2 import PdfReader, PdfWriter
import img2pdf

import fitz
import typing
import os


def extract_images(pdf_path, output_dir) -> dict:
    """Extracts images from a PDF file and saves them to an output directory.

  Args:
    pdf_path: Path to the PDF file.
    output_dir: Directory to save extracted images.
  """
    ret = {}
    reader = PdfReader(open(pdf_path, 'rb'))
    num_pages = len(reader.pages)

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        output_filename = os.path.join(output_dir, f"{page_num}-split.pdf")
        writer = PdfWriter()
        writer.add_page(page)
        writer.write(open(output_filename, 'wb'))
        ret[output_filename] = dict()
    for split_page in list(ret.keys()):
        doc = fitz.open(split_page)
        page = doc[0]
        ret[split_page]["images"] = []
        ret[split_page]["pdf_from_images"] = []
        img_id =0
        for img in page.get_images():
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            # Save image to output directory
            output_path = f"{split_page}_{img_id}_{xref}.{ext}"
            with open(output_path, "wb") as f:
                f.write(image_bytes)
                ret[split_page]["images"] += [output_path]
            with open(f"{output_path}.pdf", "wb") as f:
              f.write(img2pdf.convert([output_path]))
            ret[split_page]["pdf_from_images"]+=[output_path]
            img_id+=1
    return ret

f = "/home/vmadmin/python/cy-py/a_checking/resources/số 02 - ngày 03.01.2024.pdf"
output_dir = "/home/vmadmin/python/cy-py/a_checking/resources/result/001"
os.makedirs(output_dir,exist_ok=True)
ls = extract_images(f, output_dir)
print(ls)
