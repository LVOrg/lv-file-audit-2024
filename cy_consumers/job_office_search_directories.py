import os
import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from cyx.common import config
directory_path= config.file_storage_path
def fix_all_doc_types():
    from cyx.repository import Repository
    print(f"Sync file in {directory_path} to search engine")
    admin_app_context = Repository.apps.app('admin')
    apps = admin_app_context.context.aggregate().sort(
        admin_app_context.fields.AccessCount.desc()
    ).project(
        admin_app_context.fields.Name,
        admin_app_context.fields.NameLower,
    )
    for x in apps:
        file_context = Repository.files.app(x.Name or x.NameLower)
        total_update=0
        for ext in config.ext_office_file:
            try:
                ret = file_context.context.update(
                    file_context.fields.FileNameLower.endswith(f".{ext}") & (file_context.fields.StorageType!="Office"),
                    file_context.fields.StorageType<<"Office"
                )
                if hasattr(ret,'matched_count'):
                    total_update+=ret.matched_count
            except Exception as e:
                print(e)

        print(total_update)
# while True:
#     root_dir,list_of_sub_dir_names,list_of_file_name= next(os.walk(directory_path))
#     list_of_full_app_dirs=[ os.path.join(root_dir,x) for x in list_of_sub_dir_names if admin_app_context.context.find_one(
#         (admin_app_context.fields.NameLower==x.lower())|(admin_app_context.fields.Name==x)
#     )]
#     print(list_of_full_app_dirs)

