import os
import pathlib
from multiprocessing import Process
from cyx.media.contents import ContentsServices
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
import cy_kit
import cyx.common.msg
from cyx.common import config
from cyx.common.brokers import Broker
log_dir = os.path.join(
    pathlib.Path(__file__).parent.__str__(),
    "logs",
    cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF

)
print(f"logs to {log_dir}")
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name=pathlib.Path(__file__).stem
)
if isinstance(config.get('rabbitmq'), dict):
    cy_kit.config_provider(
        from_class=MessageService,
        implement_class=RabitmqMsg
    )
else:
    cy_kit.config_provider(
        from_class=MessageService,
        implement_class=Broker
    )
content_services = cy_kit.singleton(ContentsServices)
content, info = content_services.get_text(__file__)
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
    "files_save_search_engine.py",
    "files_ocr_pdf.py"
]

working_dir = pathlib.Path(__file__).parent.__str__()

print(working_dir)
import sys

args = [x for x in sys.argv if '=' in x]
print(args)

import subprocess
if sys.platform == "linux":
    import signal
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

task_processes = [
    subprocess.Popen(f'{sys.executable} {os.path.join(working_dir, task)} {" ".join(args)}', shell=True)
    for task
    in files_process
]
for task in task_processes:
    task.wait()
# python cy_consumers/start.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.92 rabbitmq.port=31672
