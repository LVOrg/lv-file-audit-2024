import datetime
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())

import uuid

import gradio as gr

import  libs

import os
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
  a= datetime.datetime.utcnow()
  cap = cv2.VideoCapture(video_file_path)
  n = (datetime.datetime.utcnow()-a).total_seconds()

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

  return image_file_path

os.makedirs("/socat-share",exist_ok=True)
def process_text(text,is_return_base_64_image):
    ret_file = None
    try:
        # Replace this with your desired text processing logic

        file_id = str(uuid.uuid4())
        file_download = os.path.join("/socat-share",f"{file_id}.png")
        # libs.download_file(text,file_download)

        ret_file = get_middle_frame_and_save(text,file_download)


    except Exception as ex:
        raise ex
    if is_return_base_64_image:
        return ret_file,ret_file
    else:
        return None, ret_file


iface = gr.Interface(
    fn=process_text,
    inputs=["textbox",gr.Checkbox(label="Return base64 image", value=True)],
    outputs=["image","textbox"],
    title="Text Processor",
    description="Enter text and see it processed!",

)

iface.launch(
    server_name="0.0.0.0",  # Here's where you specify server name
    server_port=1111
)
