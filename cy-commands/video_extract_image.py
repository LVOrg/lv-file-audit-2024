import cv2

print(cv2.__version__)
import os
import sys


def extract_middle_frame(input_file: str, out_put: str):
    """Extracts a frame from the middle of an MP4 video and saves it as a PNG file.

    Args:
        input_file (str): The path to the input MP4 file.

    Raises:
        FileNotFoundError: If the input file is not found.
    """

    input_file = 'http://172.16.7.99/lvfile/api/sys/admin/content-share/lv-docs/2024/03/13/mp4/6906ea59-7f88-43e3-9486-ff752bd8089d/unknown_2023.03.13-19.05 _1_.mp4?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJvb3QiLCJhcHBsaWNhdGlvbiI6ImFkbWluIn0.u2AAtdLy3sb3kfZnmIt7t9-1mhYqnb3rLGMykGQNiSg'
    cap = cv2.VideoCapture(input_file)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame_index = total_frames // 2

    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
    ret, frame = cap.read()

    if not ret:
        raise RuntimeError("Failed to read frame at index: {}".format(middle_frame_index))

    output_file = os.path.join(f"/tmp-files/{out_put}.png")
    cv2.imwrite(output_file, frame)

    print("Middle frame saved to:", output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Do extract image from file')
    parser.add_argument('input', help='Image file for OCR')
    parser.add_argument('output', help='Image file for OCR')
    parser.add_argument('verify', help='verify file for OCR')
    args = parser.parse_args()

    extract_middle_frame(args.input, args.output)
    os.system(f"echo '{args.verify}'>{args.verify}.txt")
    # python3 /cmd/video_extract_image.py "http://172.16.7.99/lvfile/api/lv-docs/file/6906ea59-7f88-43e3-9486-ff752bd8089d/unknown_2023.03.13-19.05 _1_.mp4" test test
