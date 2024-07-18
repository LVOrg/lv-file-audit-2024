import gc
import json
import mimetypes
import os.path
import pathlib
import typing
import uuid
import requests

working_dir = pathlib.Path(__file__).parent.__str__()
TEM_DIR = None

class CallAPIException(Exception):
  """
  Custom exception for errors during Web API calls.
  """

  def __init__(self, message: str, url: str = None, status_code: int = None):
    """
    Args:
        message: The error message describing the issue.
        url (optional): The URL of the Web API that caused the error.
        status_code (optional): The HTTP status code returned by the Web API, if available.
    """
    super().__init__(message)
    self.url = url
    self.status_code = status_code
    self.message=message

  def __repr__(self):
      """
          Overrides the default string representation for informative messages.
          """
      message = f"Call to Web API failed: {self.message}"
      if self.url:
          message += f"\n  URL: {self.url}"
      if self.status_code:
          message += f"\n  Status Code: {self.status_code}"
      return message
  def __str__(self):
    """
    Overrides the default string representation for informative messages.
    """
    message = f"Call to Web API failed: {self.message}"
    if self.url:
      message += f"\n  URL: {self.url}"
    if self.status_code:
      message += f"\n  Status Code: {self.status_code}"
    return message
def __verify_temp_dir__():
    global TEM_DIR
    if TEM_DIR is None:
        raise Exception("Thou should call set_temp_dir before use any method in the package")


import subprocess
import time


class ConnectionRefusedException(Exception):
    """
  Custom exception class for connection refused errors.
  """
    pass


def execute_command_with_polling(command, command_handler=None):
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
            try:
                line = process.stdout.readline().decode()
                print(line)
                if line:
                    if callable(command_handler):
                        command_handler(line)
                    else:
                        print(line, end='')  # Print without newline to avoid extra line breaks
                        ret_text += line + "\n"
            except Exception as e:
                continue
            time.sleep(0.1)  # Adjust sleep time for desired polling frequency

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
    except ConnectionRefusedException as ex:
        raise ex
    except Exception as e:
        print(e)


def set_temp_dir(dir_path: str):
    global TEM_DIR
    import os
    if os.path.isdir(dir_path):
        TEM_DIR = dir_path
    else:
        os.makedirs(TEM_DIR, exist_ok=True)
        TEM_DIR = dir_path


def new_temp_file(ext: str):
    """
    Create tem directory for processing
    :return:
    """
    global TEM_DIR
    __verify_temp_dir__()
    file_name = str(uuid.uuid4())
    ret = os.path.join(TEM_DIR, f"{file_name}.{ext}")
    return ret


def new_temp_dir():
    """
    Create tem directory for processing
    :return:
    """
    global TEM_DIR
    __verify_temp_dir__()
    dir_name = str(uuid.uuid4())
    ret = os.path.join(TEM_DIR, dir_name)
    if not os.path.isdir(ret):
        os.makedirs(ret)
    return ret


def socat_ping(port):
    ret, error = execute_command_with_polling(f"echo 'echo ok'|socat TCP4:localhost:{port} -")
    return ret, error


def call_web_api(data, action_type, url_file, download_file=None):
    """Calls a web API using the provided data.
    Args:
      data (dict): A dictionary containing API details like URL, headers, file path (optional), and response key (optional).
    :exception CallAPIException
    Returns:
        dict: The parsed JSON response data (if successful) or None (if error).
  """

    # Extract URL, headers, and file upload information

    url = data['url']
    headers = data['headers']
    # if not headers.get("Content-Type"):
    #     headers["Content-Type"] = "application/json; charset=utf-8"
    download_filename = pathlib.Path(download_file).name
    with open(url_file, "rb",download_filename=download_filename) as sf:
        sf.name = download_file
        files = {'file': sf}

        # Send the POST request
        response = requests.post(url, headers=headers, files=files)

        res_data = response.json()
        if response.status_code!=200:
            msg = json.dumps(res_data,indent=4)
            raise CallAPIException(
                message = f"{url} return error\n: {msg}",
                url=url,
                status_code=response.status_code
            )
        res_keys = data["response"].split(".")
        ret_value = res_data
        for x in res_keys:
            ret_value = ret_value[x]
        return ret_value




def get_content_from_tika(url_file:str,abs_file_path:str):
    from cyx.common import config
    import tika.parser
    import urllib.parse

    process_file = abs_file_path

    try:
        print(url_file)
        response = requests.get(url_file, stream=True)
        fx_dir= os.path.join(config.file_storage_path,"__temp_process_file__")
        os.makedirs(fx_dir,exist_ok=True)
        fx= os.path.join(fx_dir,str(uuid.uuid4()))
        if response.status_code == 200 or response.status_code==206:
            print("Download started!")
            total_size = int(response.headers.get('content-length', 0))  # Get file size from header (if available)
            downloaded = 0
            with open(fx, "wb") as file:
                for chunk in response.iter_content(1024):  # Download in chunks of 1024 bytes
                    downloaded += len(chunk)
                    file.write(chunk)
        else:
            print("rrot")
        try:
            headers = {
                'maxWriteLimit': '2147483647'
            }

            ret = tika.parser.from_file(
                filename=fx,
                serverEndpoint=config.tika_server,
                requestOptions={'headers': headers, 'timeout': 30000}
            )


            re_content = ret['content']
            del ret
            return re_content
        except Exception as ex:
            raise ex
        finally:
            os.remove(fx)
    except requests.exceptions.HTTPError as ex:
        if ex.response.status_code == 404:
            return None
        else:
            raise ex
def call_local_tika(action, action_type, url_file, download_file):
    """

    :param action:
    :param action_type:
    :param url_file:
    :param download_file:
    :return:
    """


    from cyx.common import config
    process_services_host = config.process_services_host or "http://localhost"
    import tika.parser
    import urllib.parse
    fx = os.path.join(working_dir, str(uuid.uuid4()))
    try:
        with open(url_file, "rb") as fs:
            with open(fx, "wb") as fsx:
                fsx.write(fs.read())
        try:
            headers = {
                'maxWriteLimit': '2147483647'
            }

            ret = tika.parser.from_file(
                filename=fx,
                serverEndpoint=f'{process_services_host}:9998/tika',
                requestOptions={'headers': headers, 'timeout': 30000}
            )

            # ret = parser.from_file(file_path,  requestOptions={'headers': headers, 'timeout': 30000})
            # import psutil
            # import signal
            # for x in psutil.process_iter():
            #     if x.status() == 'sleeping' and x.__name__() == 'java':
            #         os.kill(x.pid, signal.SIGKILL)
            return ret['content']
        except Exception as ex:
            raise ex
        finally:
            os.remove(fx)
    except requests.exceptions.HTTPError as ex:
        if ex.response.status_code == 404:
            return None
        else:
            raise ex


def call_socat(action, action_type, url_file, download_file):
    mime_type, _ = mimetypes.guess_type(download_file)
    port = action['port']
    command = action['command']
    ok = False
    while not ok:
        format_string = "%Y-%d-%m-%H-%M-%S"
        ret, error = socat_ping(port)
        if error is None:
            print("Start ok")
            break
        print("Try connect on next 10 second\n")
        time.sleep(10)
    print(action)

    command_id = str(uuid.uuid4())
    output_dir = os.path.join("/tmp-files")
    if not mime_type.startswith("video/"):
        with open(url_file, "rb") as sf:
            with open(download_file, "wb") as df:
                df.write(sf.read())
        cmd = action['command'].replace("{input}", f'\"{download_file}\"').replace("{output}", "\"/tmp-files\"")
    else:
        cmd = action['command'].replace("{input}", f'\"{url_file}\"').replace("{output}", "\"/tmp-files\"")
    command_full = f"echo \"{cmd} /socat-share/{command_id}\"|socat TCP4:localhost:{action['port']} -"
    ret = execute_command_with_polling(command_full)
    while not os.path.isfile(f"/socat-share/{command_id}.txt"):
        time.sleep(0.5)
    ret_data = {}
    with open(f"/socat-share/{command_id}.txt", "rb") as fs:
        ret_data = json.loads(fs.read().decode())
    os.remove(f"/socat-share/{command_id}.txt")
    if ret_data.get('error'):
        raise Exception(ret_data.get('error'))
    else:
        return ret_data.get("result")


def run_action(action, action_type, url_file, download_file):
    """
    This function will call tcp ot http server to resolve command
    if action return text content the function will return "text","...content receive after run action
    :param action:
    :param url_file:
    :param download_file:
    :return: content-type:str, content
    """
    print(action)
    if action.get('type') == "web-api":
        return call_web_api(action, action_type, url_file, download_file)
    if action.get('type') == "tika":
        return call_local_tika(action, action_type, url_file, download_file)
    elif action.get('type') == 'socat':
        return call_socat(action, action_type, url_file, download_file)
        print(action)
    else:
        raise NotImplemented("..")

from gradio_client import Client
__cache_gradio__ = {}
def get_radio_client(url:str)->Client:
    global __cache_gradio__
    if __cache_gradio__.get(url) is None:
        __cache_gradio__[url] = Client(url)
    return __cache_gradio__[url]