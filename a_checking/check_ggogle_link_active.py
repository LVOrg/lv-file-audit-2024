import cy_docs
from cyx.repository import Repository
app_context = Repository.apps.app("admin").context
data_item = app_context.find_one(Repository.apps.fields.Name=="lv-docs")
print(data_item)
client_id = data_item[Repository.apps.fields.AppOnCloud.Google.ClientId]
client_secret = data_item[Repository.apps.fields.AppOnCloud.Google.ClientSecret]
email = data_item[Repository.apps.fields.AppOnCloud.Google.Email]
refresh_token = data_item[Repository.apps.fields.AppOnCloud.Google.RefreshToken]
update_app="default"

app_context.update(
    Repository.apps.fields.Name==update_app,
    Repository.apps.fields.AppOnCloud.Google.Email<<email,
    Repository.apps.fields.AppOnCloud.Google.ClientId<<client_id,
    Repository.apps.fields.AppOnCloud.Google.ClientSecret<<client_secret,
    Repository.apps.fields.AppOnCloud.Google.RefreshToken<<refresh_token,
)
data_test = app_context.aggregate().match(
    Repository.apps.fields.Name==update_app,

).project(
    cy_docs.fields.client_id>>Repository.apps.fields.AppOnCloud.Google.ClientId,
    cy_docs.fields.client_secret>>Repository.apps.fields.AppOnCloud.Google.ClientSecret,
    cy_docs.fields.email>>Repository.apps.fields.AppOnCloud.Google.Email,
    cy_docs.fields.refresh_token>>Repository.apps.fields.AppOnCloud.Google.RefreshToken
).first_item().to_json_convertable()

for k,v in data_test.items():
    print(f"{k}:{v}")