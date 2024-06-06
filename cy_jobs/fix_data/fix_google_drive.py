import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
import traceback
import typing
from cy_jobs.cy_job_libs import JobLibs
import cy_docs
from cyx.repository import Repository


def get_list_of_app_has_google() -> typing.List[str]:
    ret = []
    agg = Repository.apps.app("admin").context.aggregate().match(
        Repository.apps.fields.AppOnCloud.Google.ClientSecret != None
    ).project(
        cy_docs.fields.app_name >> Repository.apps.fields.Name
    )
    for x in agg:
        ret += [x.app_name]
    return ret


def run():
    apps = get_list_of_app_has_google()
    for app_name in apps:
        service, error = JobLibs.google_directory_service.g_drive_service.get_service_by_app_name(app_name,
                                                                                                  from_cache=False)
        if error:
            continue
        files = Repository.files.app(app_name).context.find(
            (Repository.files.fields.google_folder_id != None) & (Repository.files.fields.FullPathOnCloud == None)
        )
        for file in files:
            folder_tree, folder_hash, error = JobLibs.google_directory_service.get_all_folders(app_name)
            if error:
                break
            for k, v in folder_hash.items():
                if v.get("id") == file[Repository.files.fields.google_folder_id]:
                    try:
                        cloud_path = "/".join(k.split('/')[1:] + [file[Repository.files.fields.FileName]])
                        Repository.files.app(app_name).context.update(
                            Repository.files.fields.Id == file.Id,
                            Repository.files.fields.FullPathOnCloud << cloud_path
                        )
                        print(f"fix {cloud_path}")
                    except Exception as ex:
                        print(traceback.format_exc())
run()