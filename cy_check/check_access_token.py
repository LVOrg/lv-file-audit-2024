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
TOKEN='EwB4A8l6BAAUAOyDv0l6PcCVu89kmzvqZmkWABkAAUvkk8cTf9uXiikc3G3mllDAqAnY37T4oQ15Yqdkr+VMJiY+5dOjSJ16/BoK212pDpVIaCvbOSqGQlYPmccFLBNFvTIJkxNiet8YXRRIGwSxkwMrYq0Ln2ytWrds1uqyCPzveMAxAfRvNP1/ORFhugnLPw3i9Bz6b9JusYNus/cRsv7j9IkyCR20vwr0tUIjho12lvhYKERX553KbX+0HmJtfwKbY2bG+nr5xKGWHmWXNlPQ7IbtZMzqKjZKhLhDqcc8wsajJOqa9tpMFTjI+2tM82D73PKNX+P1KRbQ54ObhM7dIBVlVZKH9PwXNr0syj/lS1eKdcJiiLRVpeVtp5YDZgAACAAEHpJUp1WMSALhDxBmR+yQ2zKK2mcvBsmFO3tL7owAQW8Lw0TWdAJPjzLCBJtHdgunNpJyYHSBamu0XXbIajckMT/R5jmoS1U/waSITfy3F0hg4qA/wg8MOEu8CwTh75CQC4MA3I+1LairvB2KFoPEkr+h08v4PyoZ89QwDMvJCKRQnHRl6UXYINOwBXIpWhtcXJXMVUxHii55PTjox8NnQPITC/8vI85DEGYjn/CHGBNVa2qkG56Ejoagz2cIvrsA5lC03gBZXCog7ffZD6WbS05Yv0Zkkm5kMkI9M12EmWvqcgIe4rm0uu9o1eWxdRrrHDdKTFLya9I8lHK444JFjNLnnb2hEKc6oiwkHZjMVetoUpyVkq71gZ9Ph1QV5nDsCDsaDEJzSomxhrFSxk2NyIczwsSrYyOL3tsqXYh9+UfU2E0akk0SxmtNDXjYsRVrNg3CBQtzOJOgNZXB1n0jq1oEhT1FW3XNV9a6EGfhXdakKThoxIVRnn65rX+eF05OKzaz05VWT5KtLe8mykSKR7ojUBUfwJLzA4QYLk9E9yCIM/4k9jnv9scX1Y0AVQJYyby8T90y2O63BIk4AXlIS8uFMxMjjJ6iARLeU60wE+KfP7xziMRve56AZzd11XJhAW/U/J2ja3mA+FP1lOzfgh/8zS3rS2Lp/g4nj4wHmr6XJCtyX8aSRK+4O/8X4tD++Bp1kSZfyNZxf9u+0UShYQyiw84Fc9MSsxRIlNWA7OWtJ4KSbuF4caWOmkEK14tokWfKPSF/GqmQBCp4dCQniYIC'
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