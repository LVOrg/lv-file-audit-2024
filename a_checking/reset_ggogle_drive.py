import cy_docs
from cyx.repository import Repository
apps = Repository.apps.app("admin").context.aggregate().project(
    cy_docs.fields.app_name>> Repository.apps.fields.Name
)
for x in apps:
    print(x.app_name)
    Repository.google_folders.app(x.app_name).context.delete({})
    Repository.files.app(x.app_name).context.delete(
        Repository.files.fields.StorageType=="google-drive"
    )
