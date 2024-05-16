import json
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import time
import traceback

import cy_docs
import google.auth.exceptions

from cy_jobs.cy_job_libs import JobLibs
from cyx.repository import Repository
while True:
    apps = Repository.apps.app("admin").context.aggregate().match(
        Repository.apps.fields.AppOnCloud.Google.ClientSecret!=None
    ).project(
        cy_docs.fields.data>>Repository.apps.fields.AppOnCloud.Google,
        cy_docs.fields.app_name>>Repository.apps.fields.Name
    )
    for app in apps:
        # info, error = JobLibs.google_directory_service.get_all_folder_info(app.app_name)
        # if error:
        #     print(error)
        # else:
        #     if isinstance(info.neast, dict):
        #         txt = json.dumps(info.neast, indent=4)
        #         print(txt)
        #     if isinstance(info.hash, dict):
        #         for k, v in info.hash.items():
        #             print(k)
        try:
            info,error = JobLibs.google_directory_service.get_all_folder_info(app.app_name)
            if error:
                print(error)
            else:
                if isinstance(info.neast,dict):
                    txt=json.dumps(info.neast,indent=4)
                    print(txt)
                if isinstance(info.hash,dict):
                    for k,v in info.hash.items():
                        print(k)


        except google.auth.exceptions.OAuthError:
            info, error = JobLibs.google_directory_service.get_all_folder_info(app.app_name,from_cache=False)
            if error:
                print(error)
            else:
                if isinstance(info.neast,dict):
                    txt=json.dumps(info.neast,indent=4)
                    print(txt)
                if isinstance(info.hash,dict):
                    for k,v in info.hash.items():
                        print(k)
        except Exception as ex:
            print(f"Sync directory from google-drive of app {app.app_name} is fail")
            print(traceback.format_exc())
    time.sleep(0.01)


