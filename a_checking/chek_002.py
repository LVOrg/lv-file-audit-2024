import os
import pathlib
import shutil
import  numpy
img_path = '/app/resources/test-003.png'
import cv2


def sort_by_center(rectangles):
    """Sorts a list of rectangles based on their center coordinates.

  Args:
      rectangles: A list of rectangles, where each rectangle is a tuple (x1, y1, x2, y2)
          representing the top-left and bottom-right corner coordinates of the rectangle.

  Returns:
      A new list of rectangles sorted by their center x-coordinate (primary sort)
      and then by their center y-coordinate (secondary sort).
  """

    def center_coordinate(rect):
        x1, y1, x2, y2 = rect
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    return sorted(rectangles, key=center_coordinate)


def mark_region(image_path):
    img = cv2.imread(image_path)

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)

    # Creating a copy of image
    im2 = img.copy()

    # A text file is created and flushed

    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    ret = []
    for cnt in contours:
        r = cv2.boundingRect(cnt)
        ret += [r]

    return ret


def clip_image(image_path, bounding_boxes):
    """Clips an image into separate images based on bounding boxes.

  Args:
      image_path: The path to the image file.
      bounding_boxes: A list of bounding boxes, where each box is a tuple
          (x, y, w, h) representing the top-left corner coordinates, width,
          and height of the region to clip.

  Returns:
      A list of clipped images.
  """

    # Load the image
    image = cv2.imread(image_path)

    # Clip images based on bounding boxes
    clipped_images = []
    for box in bounding_boxes:
        x, y, w, h = box
        clip = image[y:y + h, x:x + w]
        clipped_images.append(clip)

    return clipped_images


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
                if abs(rect_i[2] - rect_j[0]) <= dx and abs(rect_i[3] - rect_j[1]) <= dy:
                    # Update the combined rectangle to include both rectangles
                    combined_rect = (
                        min(rect_i[0], rect_j[0]),
                        min(rect_i[1], rect_j[1]),
                        max(rect_i[0] + rect_i[2], rect_j[0] + rect_j[2]) - min(rect_i[0], rect_j[0]),
                        max(rect_i[1] + rect_i[3], rect_j[1] + rect_j[3]) - min(rect_i[1], rect_j[1])
                    )
                    processed.add(j)

        # Add the combined rectangle to the results
        combined_rects.append(combined_rect)
        processed.add(i)

    return combined_rects


from paddleocr import PaddleOCR, draw_ocr
import cv2


ocr = PaddleOCR(use_angle_cls=True, lang="vi", show_log=False)


def detect_boxes(img_path):
    result = ocr.ocr(img_path, cls=True)
    boxes = [line[0] for line in result]
    estimate_boxes = []
    for boxe in boxes:
        corners = np.array(boxe)
        min_x = int(np.min(corners[:, 0]))  # Ensure integer for indexing
        min_y = int(np.min(corners[:, 1]))
        max_x = int(np.max(corners[:, 0])) + 1  # Add 1 for inclusive upper bound
        max_y = int(np.max(corners[:, 1])) + 1
        estimate_boxes += [(min_x, min_y, max_x, max_y)]
    return estimate_boxes


# Path to your image file


# Read the image with OpenCV
img = cv2.imread(img_path)


# for detection in results:
#     # Extract bounding box coordinates
#     corners = np.array(detection[0])
#     min_x = int(np.min(corners[:, 0]))  # Ensure integer for indexing
#     min_y = int(np.min(corners[:, 1]))
#     max_x = int(np.max(corners[:, 0])) + 1  # Add 1 for inclusive upper bound
#     max_y = int(np.max(corners[:, 1])) + 1
#     print(min_y, min_y, max_x, min_y)
#     text_boxes += [(min_y, min_y, max_x, min_y)]
    # Create a dictionary to store text and bounding box info
    # text_box = {
    #     "text": detection[1],  # Detected text
    #     "bbox": (x1, y1, x2, y2)  # Bounding box coordinates
    # }

    # text_boxes.append(text_box)
# es_rectangles = mark_region(img_path)
text_boxes = detect_boxes(img_path)
text_rectangles = combine_bound_rects(text_boxes, 100, 100)
sort_rects = sort_by_center(text_rectangles)
clipped_images = clip_image(img_path, sort_rects)
file_name = pathlib.Path(img_path).name
# print(text_rectangles)
# for rect in text_rectangles:
#     x, y, w, h = rect

dir_path = f'/app/result/{file_name}'
if os.path.isdir(dir_path):
    shutil.rmtree(dir_path)
os.makedirs(dir_path, exist_ok=True)
for i, image in enumerate(clipped_images):
    try:
        cv2.imwrite(f'/app/result/{file_name}/{i}.jpg', image)
    except:
        continue
