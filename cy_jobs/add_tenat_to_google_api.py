import cy_docs
from cyx.repository import Repository
Google = Repository.apps.app("admin").context.aggregate().match(
    Repository.apps.fields.Name=="lv-docs"
).project(

    cy_docs.fields.Google>>Repository.apps.fields.AppOnCloud.Google


).first_item()

print(Google)
Repository.apps.app("admin").context.update(
    Repository.apps.fields.Name=="default",
    Repository.apps.fields.AppOnCloud.Google<<Google.Google
)
# Repository.apps.app("admin").context.update(
#     Repository.apps.fields.Name=="masantest",
#     Repository.apps.fields.AppOnCloud.Google<<Google.Google
# )
"""
Repository.apps.fields.AppOnCloud.Google.Scope,
    Repository.apps.fields.AppOnCloud.Google.Email,
Repository.apps.fields.AppOnCloud.Google.TokenType,
Repository.apps.fields.AppOnCloud.Google.ExpiresIn,
Repository.apps.fields.AppOnCloud.Google.ClientSecret,
Repository.apps.fields.AppOnCloud.Google.AccessToken,
Repository.apps.fields.AppOnCloud.Google.ClientId,
Repository.apps.fields.AppOnCloud.Google.ClientId,
"""