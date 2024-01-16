import typing
import fitz
from PIL import Image
import os


def vertical_append_images(images_list: typing.List[str], out_put: str) -> str:
    images = []
    for image_path in images_list:
        images.append(Image.open(image_path))
    if len(images) == 0:
        return None
    total_height = sum(img.height for img in images)
    max_width = -1
    try:
        max_width = max(img.width for img in images)
    except Exception as e:
        return None

    new_image = Image.new("RGB", (max_width, total_height))
    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height
    new_image.save(out_put)
    for img_src in images_list:
        os.remove(img_src)
    return out_put
def extract_all_images_from_pdf(pdf_file, extract_to) -> typing.List[str]:
    doc = fitz.open(pdf_file)

    ret = []
    num_of_pages = len(doc)
    for page_index in range(0, num_of_pages):
        page = doc[page_index]
        image_list = page.get_images()
        # Access the first page (index starts from 0)
        image_index = 0
        image_path = os.path.join(extract_to, f"page_{page_index:04d}.png")
        image_paths = []
        for img in image_list:

            try:
                xref = img[0]  # XREF of the image object
                pix = fitz.Pixmap(doc, xref)  # Get the image as a Pixmap object
                image_bytes = None
                try:
                    image_bytes = pix.tobytes()  # Raw image data
                except:
                    new_pix = fitz.Pixmap(fitz.csRGB, pix)
                    image_bytes = new_pix.tobytes()

                    # Do something with the image data, such as saving it to a file:
                if not os.path.isdir(extract_to):
                    os.makedirs(extract_to, exist_ok=True)
                output_image = os.path.join(extract_to, f"image_{page_index}_{image_index}.png")

                with open(output_image, "wb") as f:
                    f.write(image_bytes)
                img = Image.open(output_image)
                rotated_img = img.rotate(-1 * page.rotation, expand=True)
                rotated_img.save(output_image)
                image_paths += [output_image]

            except Exception as e:
                print(e)
                pass
            image_index += 1
        if len(image_paths) == 0:
            return None
        vertical_append_images(image_paths, image_path)
        ret += [image_path]
        page_index += 1
    return ret

