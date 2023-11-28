import requests

__url__ = "https://graph.microsoft.com/v1.0/drives"


def create_directory(access_token: str,directory_name:str, driver_id: str="root"):
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }

    body = {
        "name": directory_name
    }
    response = requests.post(f"{__url__}/{driver_id}/children", headers=headers,
                             json=body)
    if response.status_code == 201:
        print("Directory created successfully")
    else:
        print("Error creating directory:", response.text)
