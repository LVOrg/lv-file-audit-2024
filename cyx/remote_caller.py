import requests
class RemoteCallerService:
    def __init__(self):
        pass

    def get_image_from_office(self, url:str, local_file, remote_file,memcache_server):
        url=url.rstrip('/')
        data = {}

        if local_file:
            # Adjust data format based on your FastAPI implementation for local file handling
            data["local_file"] = local_file
        if remote_file:
            data["remote_file"] = remote_file
        data["memcache_server"] = memcache_server

        # Send POST request with data (adjust based on your API logic)
        response = requests.post(url+"/get-image", json=data)
        try:
            return response.json()
        except:
            print(response.text)
            return dict(error=dict(Code="RemoteERR500",Description=response.text))
