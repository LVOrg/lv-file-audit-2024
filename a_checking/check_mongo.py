import cy_docs
from cyx.repository import Repository
files= Repository.files.app("hps-file-test")
items=files.context.find(
    files.fields.StorageType!="local",
    10
)
for x in items:
    print(x)