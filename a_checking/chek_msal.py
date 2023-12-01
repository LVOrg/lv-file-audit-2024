import urllib.parse
import  webbrowser
from msal import PublicClientApplication,ConfidentialClientApplication
client_id='7da41e72-1a30-48ac-a62b-8394d83cb931'
tenant_id='13d23acb-69f3-4651-98fe-76e95992f779'
client_secret ='XN88Q~FywqHbGVwFqN1eFPG5wAeYs4IiZN83JcGR'
app= ConfidentialClientApplication(client_id=client_id,client_credential=client_secret)
scopes=[
    'User.Read',
    'User.Read.All',
    'User.ReadWrite',
    'User.ReadWrite.All',
    'Files.Read',
    'Files.Read.All',
    'Files.ReadWrite',
    'Files.ReadWrite.All'
]

flow=app.get_authorization_request_url(
    scopes=scopes
)
# flow=flow.replace('/common/',f'/'+tenant_id+'/')
_r_url_=urllib.parse.quote_plus('https://172.16.13.72:8012/lvfile/api/lv-docs/azure/after_login')
url2=f'https://login.live.com/oauth20_authorize.srf?client_id={client_id}&scope=User.ReadWrite.All offline_access&response_type=code&redirect_uri={_r_url_}'
print(flow+"&redirect_uri="+urllib.parse.quote_plus('https://172.16.13.72:8012/lvfile/api/lv-docs/azure/after_login'))