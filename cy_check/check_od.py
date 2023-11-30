import onedrivesdk

redirect_uri = 'https://172.16.13.72:8012/lvfile/api/lv-docs/azure/after_login'
client_secret = 'Q__8Q~Kxk5CiHLoI~2Opwp8XtZKX7eux572ttb13'
client_id='59a42f69-9a2e-40b3-81b1-a47093b71f03'
api_base_url='https://api.onedrive.com/v1.0/'
scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

http_provider = onedrivesdk.HttpProvider()
auth_provider = onedrivesdk.AuthProvider(
    http_provider=http_provider,
    client_id=client_id,
    scopes=scopes)

client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
auth_url = client.auth_provider.get_auth_url(redirect_uri)
# Ask for the code
print('Paste this URL into your browser, approve the app\'s access.')
print('Copy everything in the address bar after "code=", and paste it below.')
print(auth_url)
# code = raw_input('Paste code here: ')
#
# client.auth_provider.authenticate(code, redirect_uri, client_secret)