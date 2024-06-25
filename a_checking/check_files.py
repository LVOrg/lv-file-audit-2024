from cyx.repository import Repository
files = Repository.files.app("lv-docs").context.find_one(
    {}
)
for f in files:
    print(f)
