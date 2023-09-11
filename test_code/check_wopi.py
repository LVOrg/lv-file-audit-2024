import pathlib
import sys
client_id = "e2cf4881-49e5-4a9e-b896-d1b73a6b89e2"
tenant_id="56590ff3-61e3-48da-9990-d4f901e87755"
secret_key=".hn8Q~IbISf9EW~j2s_eCVhf6H6KOH2oqUsAzaZG"
pwd="TnjPQhhy}&"
usr = "nttlong@lacviet365.onmicrosoft.com"

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from msal import PublicClientApplication
app_ = PublicClientApplication(
    client_id = client_id,

    authority=f"https://login.microsoftonline.com/{tenant_id}")
acc= app_.acquire_token_by_username_password(
    username=usr,
    password=pwd,
    scopes=["User.Read"]
)

from cyx.cy_wopi import wopi_discovery

app = wopi_discovery.get_app("excel")

action = wopi_discovery.get_action("WopiTest","getinfo","wopitest")
# url = wopi_discovery.get_action_url(
#     app_name="word",
#     action="view",
#     ext_file="docx",
#     wopi_source="https://codx.lacviet.vn/lvfile/api/default/file/ff7a6afb-ad73-4753-aa49-f728b455a7c7/dms_api_bo%20sung_.docx")
# print(url)