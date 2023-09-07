import requests
"""
Wednesday, September 6, 2023

Long, Nguyen Tran The	hi
	5:03 PM
Truong, Ho Nhat	sao anh
	5:04 PM
Long, Nguyen Tran The	Rãnh kg?
	5:04 PM
	Lên lầu 7 nhờ cái này cái
	
	Cái vu Azure
	
	Hôm trước làm làm sao
	
	Quên mẹ nó rồi
	
Truong, Ho Nhat	đợi e tí, e mở cái máy chương trình cũ lên đã
	5:05 PM
	We saved this conversation in the Conversations tab in Lync and in the Conversation History folder in Outlook.
	
	lyncpictplaceholder9F21D1BB-26C7-4299-8745-5FD1E5C5B5BB 
 
 

	
	client_id: 7f2fa99b-0a1e-4850-aa5f-fc6b421e078b
	
	scope:https://graph.microsoft.com/.default
	
	client_secret:iXj8Q~1wu-mdQqzVLwfZW18KSBDJfuGqBosSqcyY
	
	grant_type:client_credentials
	
	https://login.microsoftonline.com/{talentID}/oauth2/v2.0/token
	
	cái link api truyền cái TalentID vào mới dc
	
	Content-Type: application/x-www-form-urlencoded
	

"""
def get_access_token():
    """Gets the access token for the application."""
    client_id = "e2cf4881-49e5-4a9e-b896-d1b73a6b89e2"
    client_secret = "ffc6c699-40d1-4525-904e-4cedf506fca4"
    resource = "https://office.com/"
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": resource,
    }
    response = requests.post(url, data=data)
    access_token = response.json()["access_token"]
    return access_token

def main():
    access_token = get_access_token()
    url = "https://office.com/api/v1.0/me"
    headers = {
        "Authorization": "Bearer " + access_token,
    }
    response = requests.get(url, headers=headers)
    print(response.json())

if __name__ == "__main__":
    main()