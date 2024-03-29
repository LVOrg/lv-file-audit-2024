import os.path
import pathlib
import time
working_dir = pathlib.Path(__file__).parent.__str__()
from paddleocr import PaddleOCR, draw_ocr
import numpy as np
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

contents = []
import argparse


def combine_bound_rects(rects, dx, dy):
    """Combines bound rectangles together based on a distance threshold.

  Args:
      rects: A list of rectangles, where each rectangle is a tuple (x, y, w, h)
          representing the top-left corner coordinates, width, and height of the rectangle.
      dx: The maximum horizontal distance between two rectangles to be considered combined.
      dy: The maximum vertical distance between two rectangles to be considered combined.

  Returns:
      A list of combined rectangles.
  """

    # Create a dictionary to store processed rectangles to avoid revisiting them
    processed = set()
    combined_rects = []

    for i, rect_i in enumerate(rects):
        if i in processed:
            continue

        # Initialize a new combined rectangle with the current rectangle
        combined_rect = rect_i

        # Iterate through the remaining rectangles
        for j, rect_j in enumerate(rects[i + 1:]):
            if j not in processed:
                # Check if the rectangles are within the distance threshold
                if abs(rect_i[1] - rect_j[0]) <= dx and abs(rect_i[3] - rect_j[2]) <= dy:
                    # Update the combined rectangle to include both rectangles
                    combined_rect = (
                        min(rect_i[0], rect_j[0]),
                        min(rect_i[1], rect_j[1]),
                        max(rect_i[2], rect_j[2]),
                        max(rect_i[3], rect_j[3])
                    )
                    processed.add(j)

        # Add the combined rectangle to the results
        combined_rects.append(combined_rect)
        processed.add(i)

    return combined_rects




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Do OCR file')
    parser.add_argument('input', help='Image file for OCR')
    parser.add_argument('verify', help='verify file for OCR')
    args = parser.parse_args()
    img_path = args.input
    count=100
    while not os.path.isfile(img_path):
        time.sleep(0.1)
        count-=1

    if not os.path.isfile(img_path):
        print(f"{img_path} was not found")
        with open(f"{img_path}.log.txt", "wb") as fs:
            fs.write(f"{img_path} was not found")
        os.system(f"echo '{args.verify}'>{args.verify}.txt")
        exit(0)
    else:
        print(f"Do OCR file {img_path}")
        ocr = PaddleOCR(use_angle_cls=True, lang="vi", show_log=False)
        result = ocr.ocr(img_path, cls=True)
        from PIL import Image

        result = result[0]
        image = Image.open(img_path).convert('RGB')
        img_array = np.array(image)
        calculate_box = []
        if result is None:
            try:
                with open(f"{img_path}.txt", "wb") as fs:
                    fs.write("".encode())
                os.system(f"echo '{args.verify}'>{args.verify}.txt")
                exit(0)
            except Exception as e:
                print(e)
                os.system(f"echo '{args.verify}'>{args.verify}.txt")
                exit(0)
        for x in result:
            calculate_box += [x[0]]
        estimate_boxes = []
        for boxe in calculate_box:
            min_x = int(min(boxe[0][0], boxe[1][0], boxe[2][0], boxe[3][0]))  # Ensure integer for indexing
            min_y = int(min(boxe[0][1], boxe[1][1], boxe[2][1], boxe[3][1]))
            max_x = int(max(boxe[0][0], boxe[1][0], boxe[2][0],
                            boxe[3][0])) + 1  # Ensure integer for indexing + 1  # Add 1 for inclusive upper bound
            max_y = int(max(boxe[0][1], boxe[1][1], boxe[2][1], boxe[3][1])) + 1

            estimate_boxes += [(min_x, min_y, max_x, max_y)]
        # Cfg.load_config_from_file()
        config =Cfg.load_config_from_file(os.path.join(working_dir,"config-delete","base.yml"))
        # config = Cfg.load_config_from_name('vgg_transformer')
        # config.save(os.path.join(working_dir,"config-delete"))
        config['cnn']['pretrained'] = True
        config['device'] = 'cpu'
        detector = Predictor(config)
        retx_boxes = combine_bound_rects(estimate_boxes, 100, 100)
        contents = []
        for boxe in estimate_boxes:
            clipped_image = img_array[boxe[1]:boxe[3], boxe[0]:boxe[2], :]
            inspect_image = Image.fromarray(clipped_image)
            s = detector.predict(inspect_image)
            contents += [s]
        txt = " ".join(contents)
        print(f"save content to file {img_path}.txt")
        try:

            with open(f"{img_path}.txt", "wb") as fs:
                fs.write(txt.encode())
        except Exception as e:
            with open(f"{img_path}.log.txt", "wb") as fs:
                fs.write(str(e))
            print(e)
        os.system(f"echo '{args.verify}'>{args.verify}.txt")
        print("*****----finished-----*****") # important this is a accord bwteen client and server
