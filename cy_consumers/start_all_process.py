import os
import pathlib
working_folder = pathlib.Path(__file__).parent.parent.__str__()
print(working_folder)

import sys
sys.path.append(working_folder)
from multiprocessing import Process
import cy_kit
import cyx.common

log_dir = os.path.join(
    pathlib.Path(__file__).parent.__str__(),
    "logs"

)
print(f"logs to {log_dir}")
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name=pathlib.Path(__file__).stem
)
files_process = [
    "files_upload.py",
    "files_generate_image_from_video.py",
    "files_generate_image_from_office.py",
    "files_generate_image_from_pdf.py",
    "files_save_orc_pdf_file.py",
    "files_generate_thumbs.py",
    "files_generate_pdf_from_image.py",
    "files_save_default_thumb.py",
    "files_save_custom_thumb.py",
    # "files_save_search_engine.py",
    "files_ocr_pdf.py"
]

working_dir = pathlib.Path(__file__).parent.__str__()
args = [x for x in sys.argv if '=' in x]
print(args)
if sys.platform == "linux":
    import signal
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

python_path = sys.executable
def run_command(full_path):
    print(f"StarRun {full_path}")
    os.system(full_path)
process_list = []
for task in files_process:
    full_path =f"{python_path} {os.path.join(working_dir,task)} {' '.join(args)}"
    print(f"Start {full_path}")
    logs.info(f"Start {full_path}")
    p = Process(target=run_command, args=(full_path,))

    process_list+= [p]
for p in process_list:
    p.start()
for p in process_list:
    p.join()
#python cy_consumers/start_all_process.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1