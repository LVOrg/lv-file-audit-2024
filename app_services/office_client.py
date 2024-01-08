from gradio_client import Client
office_server_url= "http://172.16.13.72:8014"
file_test= f'/home/vmadmin/python/cy-py/cy_external_server/data-test/codx collaboration_userguidelist-khanh editing .docx'
client = Client(office_server_url)
url_image = client.predict(
		file_test,	# filepath  in 'name' File component
		api_name="/predict"
)
url_download = f"{office_server_url}/file={url_image}"
import requests

# Specify the URL of the file to download

response = requests.get(url_download, stream=True)  # Stream the response to avoid memory issues

# Check for successful response
if response.status_code == 200:
    # Open a local file in binary write mode
    with open(filename, "wb") as f:
        # Iterate over the response data chunks and write them to the file
        for chunk in response.iter_content(chunk_size=1024):  # Download in chunks
            f.write(chunk)

    print("File downloaded successfully!")
else:
    print("Error downloading file. Status code:", response.status_code)

#http://172.16.13.72:8014/file=/tmp/gradio/795202e536ce60624722566649b47171ee1e8b64/result/codx collaboration_userguidelist-khanh editing  2.png
print(result)