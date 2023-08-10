import cv2
import easyocr
import time
import langdetect

# Initialize the EasyOCR object
reader = easyocr.Reader(['en', 'vi'])
v_file ="/home/vmadmin/python/v6/file-service-02/bard/video/xxx.mp4"
# Open the video file
cap = cv2.VideoCapture(v_file)

# Set the start time to zero
start_time = 0

# Get the FPS
fps = cap.get(cv2.CAP_PROP_FPS)

# Initialize a list to store the captions
captions = []

# Initialize a list to store the times of the captions
times = []

# Loop over the frames in the video
frame_index=0
while True:
    # Read the next frame
    ret, frame = cap.read(frame_index)

    # If the frame is not read successfully, break
    if not ret:
        break

    # Detect and recognize text in the frame
    texts = reader.readtext(frame,detail=0)
    text = " ".join(texts)

    # Check if the text is a caption

    if len(text) > 10:
            # Detect the language of the text
            language = langdetect.detect(text)

            # Check if the language is in the list of languages
            if language not in ["en", "vi"]:
                continue

        # Calculate the time in seconds
    time_in_seconds = start_time + (fps * frame_index)
    frame_index += fps*5

    # Add the caption to the list of captions
    captions.append(text)

    # Add the time of the caption to the list of times
    times.append(time_in_seconds)

# Close the video file
cap.release()

# Print the captions and their times
for caption, time in zip(captions, times):
    print("{} ({})".format(caption, time))