import sys
import pathlib
sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import os.path

from fastapi import FastAPI
import tempfile
temp_path = os.path.join(pathlib.Path(__file__).parent.__str__(),"tmp-upload")
os.makedirs(temp_path,exist_ok=True)
tempfile.tempdir = temp_path
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image  # Assuming processing involves using Pillow library
app = FastAPI()
import io
@app.get("/")
async def root():
    return {"message": "Hello World!"}
@app.post("/image-from-office")
async def image_from_office(officeFile: UploadFile = File(...)):
    content = await officeFile.read()

    # Open the image using Pillow
    # img = Image.open(io.BytesIO(content))

    # Perform your desired image processing here (optional)
    # For example, resizing:
    # resized_img = img.resize((256, 256))

    # Return the image data (modify based on your needs)
    # Option 1: Return the raw bytes
    # return content

    # Option 2: Return the processed image data (if applicable)
    # io_obj = io.BytesIO()
    # resized_img.save(io_obj, format=img.format)
    # return io_obj.getvalue()

    # Option 3: Return a JSON response with image information
    return {
        "filename": officeFile.filename,
        "content_type": officeFile.content_type,
        # Add information about processed image here (if applicable)
        # "width": resized_img.width,
        # "height": resized_img.height,
    }
if __name__ == "__main__":
    uvicorn.run("office:app", host="0.0.0.0", port=8001)