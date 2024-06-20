import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
import time
import traceback

import cy_docs


from cy_jobs.cy_job_libs import JobLibs
from cyx.repository import Repository
import pymongo.errors
if __name__ == "__main__":
    while True:
        try:
            apps = Repository.apps.app("admin").context.aggregate().match(
                Repository.apps.fields.AppOnCloud.Google.ClientSecret!=None
            ).project(
                cy_docs.fields.app_name>>Repository.apps.fields.Name
            )

            for app in apps:

                app_name = app.app_name

                folder_tree, folder_hash, error = JobLibs.google_directory_service.get_all_folders(app_name,include_file=False)
                if error:
                    time.sleep(1)
                    continue
                for k,v in folder_hash.items():
                    try:
                        Repository.cloud_path_track.app(app_name=app_name).context.insert_one(
                            Repository.cloud_path_track.fields.CloudPath<< f"Google/{k}",
                            Repository.cloud_path_track.fields.CloudPathId<<v
                        )
                    except pymongo.errors.DuplicateKeyError as ex:
                        if hasattr(ex,"details") and isinstance(ex.details,dict) and  ex.details.get('keyPattern',{}).get('CloudPath'):
                            continue

                    except Exception as ex:
                        print(ex)
        except Exception as ex:
            print(traceback.format_exc())
        finally:
            JobLibs.malloc_service.reduce_memory()
        time.sleep(1)

