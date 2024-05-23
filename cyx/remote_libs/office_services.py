import requests
import os
class OfficeService:
    def __init__(self):
        pass

    def get_image_of_file(self, host, file_path):
        with open(file_path, "rb") as fs:
            image_data = fs.read()

        # Prepare the request data
            files = {"officeFile": (os.path.basename(file_path), image_data)}

            # Send the POST request with the image file
            response = requests.post(host, files=files,stream=True)

            if response.status_code == 200:
                # Process the response data based on your chosen return type in the API
                data = response.json()  # Assuming Option 3 (JSON response) in the API code
                print(f"Filename: {data['filename']}")
                print(f"Content Type: {data['content_type']}")
                # Access other data from the response if applicable (e.g., processed image dimensions)
            else:
                print(f"Error uploading image: {response.text}")