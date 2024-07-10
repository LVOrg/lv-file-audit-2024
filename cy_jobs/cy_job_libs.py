import hashlib
import pathlib
import threading
import time
import traceback

import cy_kit
import cy_file_cryptor.wrappers
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.temp_file import TempFiles

temp_file = cy_kit.singleton(TempFiles)
# from cyx.loggers import LoggerService
from cyx.content_services import ContentService, ContentTypeEnum
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
import cy_utils
import cy_utils.texts
import mimetypes
from cy_xdoc.services.search_engine import SearchEngine
import gradio_client

print(gradio_client.__version__)
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
from gradio_client import Client
from cyx.processing_file_manager_services import ProcessManagerService
from cyx.google_drive_utils.directories import GoogleDirectoryService
from cyx.common import config
import cy_file_cryptor.context
from kazoo.client import KazooClient
from memcache import Client as MClient
import requests
import multiprocessing
import resource


def run_with_limited_memory(target, args, memory_limit=1024 * 1024 * 100):
    # Set the memory resource limit for the process
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

    # Create a Process object
    process = multiprocessing.Process(target=target, args=args)

    # Start the process
    process.start()

    # Wait for the process to finish (optional)
    process.join()


def check_memcache():
    ok = False
    while not ok:
        try:
            cache_server = config.cache_server
            print(f"Connect to {cache_server}")
            client = MClient(tuple(cache_server.split(":")))
            ok = client.set("test", "ok")
        except Exception as e:
            print(f"Error connecting to Memcached: {e}")
    print(f"Memcache server is ok run on {config.cache_server}")


check_memcache()

cy_file_cryptor.context.set_server_cache(config.cache_server)
import cy_file_cryptor.wrappers
from cyx.malloc_services import MallocService

class JobLibs:
    shared_storage_service: ShareStorageService = cy_kit.singleton(ShareStorageService)
    content_service: ContentService = cy_kit.singleton(ContentService)
    # logger=cy_kit.singleton(LoggerService),
    local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService)
    search_engine = cy_kit.singleton(SearchEngine)
    process_manager_service: ProcessManagerService = cy_kit.singleton(ProcessManagerService)
    azure_utils_services: AzureUtilsServices = cy_kit.singleton(AzureUtilsServices)
    google_directory_service: GoogleDirectoryService = cy_kit.singleton(GoogleDirectoryService)
    malloc_service = cy_kit.singleton(MallocService)

    @staticmethod
    def get_doc_type(file_ext: str) -> str:
        file_ext = file_ext.lower()
        mime_type, _ = mimetypes.guess_type(f"a.{file_ext}")
        if mime_type.startswith("image/"):
            return "image"
        elif file_ext.lower() == "pdf":
            return "pdf"
        elif mime_type.startswith("video/"):
            return "video"
        elif file_ext in config.ext_office_file:
            return "office"
        else:
            return "unknown"

    @staticmethod
    def do_process_content(action_info: dict, download_url: str, download_file: str):
        """
        Call external service for content processing
        :param action_info:
        :param download_url:
        :param download_file:
        :exception cy_utils.CallAPIException
        :return:
        """

        action = action_info['content']
        content = None
        if action['type'] == 'tika':
            content = cy_utils.call_local_tika(
                action=action,
                action_type="content",
                url_file=download_url,
                download_file=""
            )
        elif action['type'] == 'web-api':
            content = cy_utils.call_web_api(
                data=action,
                action_type="content",
                url_file=download_url,
                download_file=download_file
            )
        return content


import subprocess


def print_task_progress(tasks):
    """Prints task progress in a console-friendly format with limits.

  Args:
      tasks: A dictionary where keys are task names (e.g., "task1", "task2")
             and values are lists of progress messages for each task.
  """

    for task_name, messages in tasks.items():
        print(task_name + ":")
        for i, message in enumerate(messages):
            if i < 20:  # Limit to 20 lines
                print(f"  {message}")
            else:
                print(f"  ... (showing only the first 20 lines)")
                break  # Exit the inner loop after 20 lines


task_running = dict()


def execute_command_with_polling(command):
    """
  Executes a command line and prints output while it's running.

  Args:
      command: A string representing the command to execute.
  """
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        ret_text = ""
        while process.poll() is None:
            # Check for new output periodically (adjust interval as needed)
            file_path = command.split(' ')[1]
            try:
                line = process.stdout.readline().decode()
                print(command+":\n")
                print("\t"+line)
                # if line !='\n':
                #     screen_logs(file_path, line)

            except Exception as ex:
                screen_logs(file_path, traceback.format_exc())
            time.sleep(0.3)  # Adjust sleep time for desired polling frequency

        # Wait for the command to finish and get the final output
        output, error = process.communicate()
        if output and output != bytes([]):
            try:
                if "Connection refused" in output.decode():
                    return None, output.decode()
                else:
                    return ret_text, None

            except Exception as e:
                raise e
        if "Connection refused" in ret_text:
            return None, ret_text
        return ret_text, None
    except Exception as ex:
        raise ex


def execute_file(excute_file: str, args, python_path: str = "python3"):
    import subprocess
    # command = [python_path, excute_file] + args
    # Define the command to run
    print(excute_file)

    def running(excute_file: str, args, python_path: str):
        command = [python_path, excute_file] + args
        # execute_command_with_polling(" ".join(command))
        output = subprocess.run(command, capture_output=True, text=True)

        print(output.stdout)

    th = threading.Thread(target=running, args=(excute_file, args, python_path,))
    # th.run()
    return th
    # execute_command_with_polling(" ".join(command))


from cyx.cache_service.memcache_service import MemcacheServices

key = hashlib.sha256(__file__.encode()).hexdigest()+"test"
screen_logs_cache = cy_kit.singleton(MemcacheServices)

screen_logs_cache.remove(key)
from cyx.log_watcher_service import LogWatcherServices
log_watcher_services = cy_kit.singleton(LogWatcherServices)
LIMIT_LINES=10
def screen_logs(monitor: str, content: str, max_lines=1):
    log_watcher_services.logs(content)


def print_screen_logs(max_lines=1):
    global key
    def run():
        while True:
            time.sleep(0.5)
            print("\033c", end="")
            ret = screen_logs_cache.get_dict(key)
            if not ret:
                ret = dict()
            for k, v in ret.items():
                print(k + ":\n")
                for x in v.split('\n')[-5:]:
                    if x.strip(' ').lstrip(' ').rstrip(' '):
                        print('\t' + x)
                v = '\n'.join(v.split('\n')[-5:])
                ret[k] = v
            screen_logs_cache.set_dict(key, ret)
    threading.Thread(target=run).start()



from multiprocessing import Process


def run_all(execute_files, side_kick_path, args):
    app_path = pathlib.Path(__file__).parent.__str__()
    fx = [" ".join([side_kick_path, app_path + "/" + x, " ".join(args)]) for x in execute_files]
    # for x in execute_files:
    #     screen_logs(app_path + "/" + x,f"Start {x}")

    full_command = " & ".join(fx)
    print(full_command)

    # execute_command_with_polling(full_command)
    prs = []
    for x in fx:
        prs += [threading.Thread(target=execute_command_with_polling, args=(x,))]
    for p in prs:
        p.start()
    for p in prs:
        p.join(2)
"""
import ctypes
libc = ctypes.CDLL("libc.so.6")
libc.malloc_trim(0)
"""
import ctypes
libc = ctypes.CDLL("libc.so.6")

libc.malloc_trim(0)