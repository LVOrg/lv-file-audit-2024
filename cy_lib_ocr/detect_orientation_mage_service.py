import os.path
import pathlib
import subprocess
import gc



# try:
#     subprocess.run(["pip", "install", "pytesseract"], check=True)
#     subprocess.run("apt install tesseract-ocr -y".split(" "),check=True)
#     """
#     pip install opencv-contrib-python==3.4.2.16
#     pip install opencv-python==3.4.2.16
#     apt update
#     """
#     # subprocess.run("apt update".split(" "), check=True)
#     # subprocess.run("apt upgrade python3-opencv -y".split(" "), check=True)
#     # subprocess.run("pip install opencv-python==3.4.2.16".split(" "), check=True)
#     print("pytesseract installed successfully!")
# except subprocess.CalledProcessError as e:
#     print("Error installing pytesseract:", e)
import cv2
import pytesseract
from icecream import ic
import numpy as np
class OrientDetector:
    def __init__(self):
        pass



    def rotate_image(self,image_path, angle):
        """Rotates an image by the specified angle.

        Args:
            image_path (str): Path to the image file.
            angle (int): Rotation angle in degrees (90, 180, or 270).

        Returns:
            numpy.ndarray: The rotated image.
        """

        # Load the image
        img = cv2.imread(image_path)

        # Load the image
        img = cv2.imread(image_path)

        # Calculate the rotation matrix
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)

        # Calculate the new dimensions of the rotated image
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_width = int(height * sin + width * cos)
        new_height = int(height * cos + width * sin)


        # Adjust the rotation matrix to account for the new dimensions
        rotation_matrix[0, 2] += (new_width - width) / 2
        rotation_matrix[1, 2] += (new_height - height) / 2

        # Rotate the image
        rotated_img = cv2.warpAffine(img, rotation_matrix, (new_width, new_height))

        out_put_dir = pathlib.Path(image_path).parent.__str__()
        file_name = pathlib.Path(image_path).stem
        ext = pathlib.Path(image_path).stem
        out_put_file_path = os.path.join(out_put_dir, f"{file_name}.{angle if angle>0 else -angle}.jpg")
        cv2.imwrite(out_put_file_path, rotated_img)
        return out_put_file_path



    def deskew(self,image_path):
        """Deskews an image using OpenCV.

        Args:
            img (numpy.ndarray): The input image.

        Returns:
            numpy.ndarray: The deskewed image.
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=10, maxLineGap=20)

        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)

        if angles:
            median_angle = np.median(angles)
            angle_in_degrees = int(np.rad2deg(median_angle))
            print("Skew angle:", angle_in_degrees)

            if angle_in_degrees > 0:
                angle_in_degrees = -angle_in_degrees

            height, width = img.shape[:2]
            center = (width // 2, height // 2)
            M = cv2.getRotationMatrix2D(center, -1*angle_in_degrees, 1)
            rotated_img = cv2.warpAffine(img, M, (width, height))
            out_put_dir = pathlib.Path(image_path).parent.__str__()
            file_name = pathlib.Path(image_path).stem
            ext = pathlib.Path(image_path).stem
            out_put_file_path = os.path.join(out_put_dir, f"{file_name}.deskewed.jpg")

            cv2.imwrite(out_put_file_path, rotated_img)
            return out_put_file_path
        else:
            ic("No lines detected.")
            return image_path

    def deskew_1(self,image_path):
        """Deskews an image using OpenCV.

        Args:
            img (numpy.ndarray): The input image.

        Returns:
            numpy.ndarray: The deskewed image.
        """
        img = cv2.imread(image_path)
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to create a binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour (assuming it's the desk)
        largest_contour = max(contours, key=cv2.contourArea)

        # Fit a rectangle to the contour
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Calculate the angle of the rectangle
        angle = np.arctan2(box[1][1] - box[0][1], box[1][0] - box[0][0]) * 180 / np.pi

        # Rotate the image by the calculated angle
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1)
        rotated_img = cv2.warpAffine(img, M, (width, height))

        out_put_dir = pathlib.Path(image_path).parent.__str__()
        file_name = pathlib.Path(image_path).stem
        ext = pathlib.Path(image_path).stem
        out_put_file_path = os.path.join(out_put_dir, f"{file_name}.deskewed.jpg")

        cv2.imwrite(out_put_file_path, rotated_img)
        return out_put_file_path



    def detect_text_orientation(self,image_path):
        """Detects the text orientation in an image.

        Args:
            image_path (str): Path to the image file.

        Returns:
            int: Text orientation angle (90, 180, or 270).
        """

        # Load the image
        img = cv2.imread(image_path)

        # Preprocess the image (e.g., grayscale, thresholding, etc.) if necessary
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Perform text detection using Tesseract
        text = pytesseract.image_to_string(thresh, config='--psm 6')

        # Analyze the detected text for orientation clues
        if len(text) > 0:
            # Check for inverted text (common indicator of 180-degree rotation)
            if text.islower():
                return 180

            # Check for rotated text (common indicator of 90 or 270-degree rotation)
            # Analyze the bounding boxes of detected words or characters
            boxes = pytesseract.image_to_boxes(thresh)
            if boxes:
                # Calculate the average angle of the bounding boxes
                angles = []
                ic("detect image orientation")
                for box in boxes.splitlines():
                    # ic(box.split())
                    conf, text,x1, y1, x2, y2  = box.split()

                    x1= float(x1)
                    y1 = float(y1)
                    x2 = float(x2)
                    y2 = float(y2)




                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    angles.append(angle)
                avg_angle = np.mean(angles)

                # Determine the orientation based on the average angle
                if -45 <= avg_angle <= 45:
                    del img
                    gc.collect()
                    return self.detect_text_orientation_by_lines(image_path)  # No rotation
                elif 45 < avg_angle <= 135:
                    del img
                    gc.collect()
                    return 180+self.detect_text_orientation_by_lines(image_path)   # 270-degree rotation
                elif -135 <= avg_angle < -45:
                    del img
                    gc.collect()
                    return self.detect_text_orientation_by_lines(image_path)  # 90-degree rotation
                else:
                    del img
                    gc.collect()
                    return 180+self.detect_text_orientation_by_lines(image_path)   # 180-degree rotation

        # If no text is detected, return 0 or an error indication
        return 0  # Indicate no detectable text orientation
    def detect_text_orientation_by_lines(self,image_path):
        """Detects the text orientation in an image.

        Args:
            image_path (str): Path to the image file.

        Returns:
            int: Text orientation angle (90, 180, or 270).
        """

        # Load the image
        img = cv2.imread(image_path)

        # Preprocess the image (e.g., grayscale, thresholding, etc.) if necessary
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Perform text detection using Tesseract
        text = pytesseract.image_to_string(thresh, config='--psm 6')

        # Analyze the detected text for orientation clues
        if len(text) > 0:
            # Check for inverted text (common indicator of 180-degree rotation)
            if text.islower():
                del img
                gc.collect()
                return 180
            else:
                del img
                gc.collect()
                # Check for rotated text (common indicator of 90 or 270-degree rotation)
                # You can add more heuristics or machine learning techniques for more precise detection
                # For example, analyze the bounding boxes of detected words or characters
                return 90  # Assuming 90 degrees is more common than 270 degrees
        else:
            del img
            gc.collect()
            # If no text is detected, return 0 or an error indication
            return 0  # Indicate no detectable text orientation
    def pre_process_image(self,image_path):
        angle = self.detect_text_orientation(image_path)
        rota_image = self.rotate_image(image_path,-1*angle)
        return rota_image




def main():
    test_file = "/app/a_checking/resource-test/test-001/p2-65.png"
    svc = OrientDetector()
    ret = svc.pre_process_image(test_file)
    print(ret)


if __name__ == "__main__":
    main()
# docker run -it  -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app -v /mnt/files:/mnt/files docker.lacviet.vn/xdoc/composite-ocr:2.2.1 /bin/bash
# # python /app/cy_lib_ocr/detect_orientation_mage_service.py
