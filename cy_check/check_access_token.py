import requests
import json
import urllib
scopes=[
                        'https://graph.microsoft.com/user.read',
                        'https://graph.microsoft.com/Files.ReadWrite.All',
                        'https://graph.microsoft.com/Files.ReadWrite']
from ms_od_fwcking import utils
__scope_str__ = urllib.parse.quote(" ".join(scopes), 'utf8')
secret_value='qO38Q~QE_YZceT_43wamVnejemg5dFl3bd5N~cBc'
client_id='72ea309b-170a-41a1-b399-af323d58ca35' #de8bc8b5-d9f9-48b1-a8ad-b748da725064
tenant_id='13a53f39-4b4d-4268-8c5e-ae6260178923'
# client_id="c44b4083-3bb0-49c1-b47d-974e53cbdf3c"

URL = f"https://login.windows.net/{tenant_id}/oauth2/token?api-version=v1.0&scope={__scope_str__}"

TOKEN =utils.get_access_token_key(client_id=client_id,tenant_id=tenant_id,secret_value=secret_value)
ret=utils.get_all_users_profiles(token=TOKEN)
# ret=utils.get_user_profile(token=TOKEN,user_id='f63c97e9-6c9f-43df-b263-351ae944dea1')
ret=utils.get_all_folders_of_user(token=TOKEN,user_id='944bf55c-0782-4d3e-9711-f95e07460511')
print(ret)
import onedrivesdk

redirect_uri = 'http://localhost:8080/'
client_secret = 'your_client_secret'
client_id='your_client_id'
api_base_url='https://api.onedrive.com/v1.0/'
scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

http_provider = onedrivesdk.HttpProvider()
auth_provider = onedrivesdk.AuthProvider(
http_provider=http_provider,
client_id=client_id,
scopes=scopes)

client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
auth_url = client.auth_provider.get_auth_url(redirect_uri)