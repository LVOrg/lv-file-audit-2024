import json
import pathlib
import sys
import threading
import traceback



sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append("/app")
from cy_jobs.jobs import task_content
from cy_jobs.jobs import task_google_folder_sync

content_thread = threading.Thread(target=task_content.run,args=())
task_google_folder_sync_thead = threading.Thread(target=task_google_folder_sync.run)
task_google_folder_sync_thead.run()
# def run_all(theads):
#     for th in theads:
#         if isinstance(th,threading.Thread):
#             th.start()
#     for th in theads:
#         if isinstance(th,threading.Thread):
#             th.join(5)
# from cy_jobs.cy_job_libs import run_with_limited_memory
# run_with_limited_memory(target=run_all,args=(
#     [content_thread,task_google_folder_sync_thead],
# ),memory_limit=1024*1024*1024*2)