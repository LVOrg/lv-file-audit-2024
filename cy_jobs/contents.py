import json
import os.path
import pathlib
import sys
import threading
import traceback


runtime_args = [x for x in  sys.argv[1:] if len(x.split('=')[1])>0]
print(runtime_args)
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append("/app")
# from cy_jobs.jobs import task_content
# from cy_jobs.jobs import task_google_folder_sync
# from cy_jobs.fix_data import fix_google_drive
app_path= pathlib.Path(__file__).parent.__str__()
execute_files = [
    "fix_data/fix_google_drive.py",
    "jobs/task_content.py",
    # "jobs/task_google_driver_folders.py",
    "jobs/task_google_file_sync.py",
    "jobs/task_onedrive_file_sync.py",
    "jobs/task_images_from_office.py",
    "jobs/task_images_from_office.py",
    "web.py"
]

from cy_jobs import cy_job_libs
from cy_jobs.cy_job_libs import print_screen_logs
if __name__ == "__main__":
    cy_job_libs.run_all(execute_files=execute_files,args=runtime_args, side_kick_path="python3")


