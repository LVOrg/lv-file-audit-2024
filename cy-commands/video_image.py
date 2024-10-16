import argparse
import json
import pathlib
import subprocess
import sys
import os
import uuid

import cv2
def get_middle_frame_and_save(video_file_path, image_file_path):
  """Extracts the middle frame from a video, converts it to PNG, and saves it.

  Args:
      video_file_path (str): Path to the input video file.
      image_file_path (str): Path to save the extracted frame (PNG format).

  Raises:
      ValueError: If the video file cannot be opened or the frame count cannot be retrieved.
  """

  # Open the video capture object
  cap = cv2.VideoCapture(video_file_path)

  # Check if video was opened successfully
  if not cap.isOpened():
    raise ValueError("Error opening video file:", video_file_path)

  # Get the total number of frames
  total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

  # Check if frame count retrieval was successful
  if total_frames is None:
    raise ValueError("Could not retrieve frame count for video:", video_file_path)

  # Determine the index of the middle frame, handling odd or even total frames
  middle_frame_index = int(total_frames / 2) if total_frames % 2 == 0 else int((total_frames - 1) / 2)

  # Seek to the middle frame
  if not cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index):
    print("Warning: Unable to seek to the exact middle frame. Using closest available frame.")

  # Capture the middle frame
  ret, frame = cap.read()

  # Check if a frame was successfully read
  if not ret:
    raise ValueError("Error reading frame from video:", video_file_path)

  # Ensure the output directory exists (create it if necessary)
  os.makedirs(os.path.dirname(image_file_path), exist_ok=True)  # Create directories if they don't exist

  # Save the frame as a PNG image
  cv2.imwrite(image_file_path, frame)

  # Release the video capture object
  cap.release()

  print(f"Middle frame extracted and saved to: {image_file_path}")

def main():
  """Parses command-line arguments and calls the get_middle_frame_and_save function."""
  try:
    parser = argparse.ArgumentParser(description='Do OCR file')
    parser.add_argument('input', help='Image file for OCR')
    parser.add_argument('output', help='Image file for OCR')
    parser.add_argument('verify', help='verify file for OCR')
    # parser = argparse.ArgumentParser(description="Extract middle frame from video and save as PNG.")
    # parser.add_argument("video_file_path", type=str, help="Path to the input video file.")
    # parser.add_argument("ouput", type=str, help="Path to save the extracted frame (PNG format).")

    args = parser.parse_args()
    video_file = args.input

    image_path = os.path.join(args.output,f"{str(uuid.uuid4())}.png")
    print(f"process file at {video_file} in to {image_path}")
    get_middle_frame_and_save(video_file, image_path)
    ret = dict(
      result=image_path
    )
    with open(f"{args.verify}.txt", "wb") as ret_fs:
      ret_fs.write(json.dumps(ret).encode())

    print(f"generate image from {args.input} ... to {args.output} successfully!")
  except Exception as error:
    str_error = str(error)
    ret = dict(
      error=str_error
    )
    with open(f"{args.verify}.txt", "wb") as ret_fs:
      ret_fs.write(json.dumps(ret).encode())
    print(f"generate image from {args.input} ... to {args.output} fail!", error)

if __name__ == "__main__":
  main()