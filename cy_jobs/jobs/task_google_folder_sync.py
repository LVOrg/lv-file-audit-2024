import os.path

import cy_docs
import google.auth.exceptions
from cy_jobs.cy_job_libs import JobLibs
from cyx.repository import Repository
import json
import traceback
import time
def run():
    local_dir=None
    while True:
        apps = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.AppOnCloud.Google.ClientSecret != None
        ).project(
            cy_docs.fields.data >> Repository.apps.fields.AppOnCloud.Google,
            cy_docs.fields.app_name >> Repository.apps.fields.Name
        )
        for app in apps:
            try:
                info, error = JobLibs.google_directory_service.get_all_folder_info(app.app_name)
                if error:
                    print(error)
                    continue
                else:
                    if isinstance(info.hash, dict):
                        for k, v in info.hash.items():
                            # local_dir= os.path.join("/mnt/files/__cloud_directories_sync__",app.app_name,k.split('/')[1:])
                            dirs = k.split('/')[1:]
                            if len(dirs)>0:
                                local_dir = os.path.join("/mnt/files/__cloud_directories_sync__", app.app_name,
                                                         "/".join(dirs))
                                if not os.path.isfile(local_dir):
                                    os.makedirs(local_dir,exist_ok=True)
                                import hashlib
                                file_name = hashlib.sha256(local_dir.encode()).hexdigest()
                                if_folder_file_path = os.path.join(local_dir,file_name)+".txt"
                                if isinstance(v.get("id"),str):
                                    if not os.path.isfile(if_folder_file_path):
                                        with open(if_folder_file_path,"wb") as f:
                                            f.write(v.get("id").encode())
                            print(k.split('/')[1:])


            except google.auth.exceptions.OAuthError:
                info, error = JobLibs.google_directory_service.get_all_folder_info(app.app_name, from_cache=False)
                if error:
                    print(error)
                else:
                    if isinstance(info.neast, dict):
                        txt = json.dumps(info.neast, indent=4)
                        print(txt)
                    if isinstance(info.hash, dict):
                        for k, v in info.hash.items():
                            print(k)
            except Exception as ex:
                print(f"Sync directory from google-drive of app {app.app_name} is fail")
                print(traceback.format_exc())
        time.sleep(30)