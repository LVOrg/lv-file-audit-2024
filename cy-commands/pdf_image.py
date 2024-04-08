import fitz
import pathlib
import os
import glob
import argparse
import json

def get_image(file_path: str,to_dir:str):
    pdf_file = file_path
    filename_only = pathlib.Path(pdf_file).stem
    to_file = os.path.join(to_dir,f"{filename_only}.png")
    unique_dir = pathlib.Path(file_path).parent.__str__()

    image_file_path = os.path.join(unique_dir, f"{filename_only}.png")
    if os.path.isfile(image_file_path):
        return image_file_path
    if os.path.isfile(image_file_path):
        return image_file_path
    # To get better resolution
    zoom_x = 2.0  # horizontal zoom
    zoom_y = 2.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
    all_files = glob.glob(pdf_file)
    for filename in all_files:
        doc = fitz.open(filename)  # open document
        for page in doc:  # iterate through the pages
            pix = page.get_pixmap()  # render page to an image
            pix.save(to_file)  # store image as a PNG
            break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
        break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
    return to_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Do OCR file')
    parser.add_argument('input', help='Image file for OCR')
    parser.add_argument('output', help='Image file for OCR')
    parser.add_argument('verify', help='verify file for OCR')
    args = parser.parse_args()
    try:
        if not os.path.isfile(args.input):
            raise FileNotFoundError(args.input)
        print(f"generate image from {args.input} ... to {args.output}")
        ret_file = get_image(args.input,args.output)
        ret = dict(
            result=ret_file
        )
        with open(f"{args.verify}.txt", "wb") as ret_fs:
            ret_fs.write(json.dumps(ret).encode())
    except Exception as error:
        str_error = str(error)
        ret = dict(
            error=str_error
        )
        with open(f"{args.verify}.txt", "wb") as ret_fs:
            ret_fs.write(json.dumps(ret).encode())
        print(f"generate image from {args.input} ... to {args.output} fail!", error)

