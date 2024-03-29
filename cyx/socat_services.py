import os.path
import subprocess
import threading
import time
import typing
import uuid
import datetime

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
        return ret_text,None
    except ConnectionRefusedException as ex:
        raise ex
    except Exception as e:
        print(e)
class SocatClientService:
    def __init__(self):
        self.process = None
        self.port = 8765

    def start(self, port):
        ok= False
        while not ok:
            format_string = "%Y-%d-%m-%H-%M-%S"
            ret, error = self.ping()
            if error is None:
                print("Start ok")
                return
            print("Try connect on next 10 second\n")
            time.sleep(10)





    def send(self,cmd:str):
        command_id = str(uuid.uuid4())
        """
            python3.9 /cmd/ocr.py /tmp-files/19f1eba9-7664-46a1-8f43-40af9618cf66.png &  # Run ocr.py in background
            process_id=$!  # Capture the process ID of the background job

            wait $process_id  # Wait for the background job to finish
            
            if [ $? -eq 0 ]; then
              echo "Successful" > /socat-share/19ac17f4-7057-4683-8fa1-7a0dcd50f527.txt
            else
              echo "Error" > /socat-share/19ac17f4-7057-4683-8fa1-7a0dcd50f527.txt
            fi
        """
        #python3.9 /cmd/ocr.py /tmp-files/19f1eba9-7664-46a1-8f43-40af9618cf66.png >&2> /socat-share/19ac17f4-7057-4683-8fa1-7a0dcd50f527.txt

        command_template=(f"{cmd}\n"
                          f"if [ $? -ne 0 ]; then\n"
                          f"echo 'Error'>/socat-share/{command_id}.txt\n"
                          f"else\n"
                          f"echo 'Successful'>/socat-share/{command_id}.txt\n"
                          f"fi\n"
                          f" while [[ ! -f \"/socat-share/{command_id}.txt\" ]]; do\n"
                          f"echo \"Waiting for file: /socat-share/{command_id}.txt...\"\n"
                          f"sleep 1\n"
                          f"done")
        """
        trap '[[ $? -eq 0 ]] && echo "Successful" || echo "Error"; echo $! > /tmp/ocr_pid.txt' EXIT

            python3.9 /cmd/ocr.py /tmp-files/0b17af96-54b8-4bdc-b57e-6acef050e4cf.png

            # Optional: Get the process ID from the temporary file
            process_id=$(cat /tmp/ocr_pid.txt)
            
            # Optional: Wait for the process to finish using the ID (uncomment if needed)
            # wait $process_id
            
            # Optional: Remove the temporary file (uncomment if needed)
            # rm /tmp/ocr_pid.txt
            
            while [[ ! -f "$file_path" ]]; do
  echo "Waiting for file: $file_path..."
  sleep 5  # Adjust sleep time as needed (seconds)
  done

        """
        # command_template=(f"trap '[[ $? -eq 0 ]] && echo \"Successful\" || echo \"Error\"; echo $! > /socat-share/{command_id}.txt' EXIT\n"
        #                   f"{cmd}\n"
        #                   f" while [[ ! -f \"/socat-share/{command_id}.txt\" ]]; do\n"
        #                   f"echo \"Waiting for file: /socat-share/{command_id}.txt...\"\n"
        #                   f"sleep 1\n"
        #                   f"done")
        command_template = command_template.replace('"','\\"')
        command_full= f"echo \"{command_template}\"|socat TCP4:localhost:3456 -"
        command_full = f"echo \"{cmd} /socat-share/{command_id}\"|socat TCP4:localhost:3456 -"
        ret =execute_command_with_polling(command_full)
        # cmd_check=f"echo 'Xong'>//socat-share/{command_id}.txt"
        # command_check = f"echo \"{cmd_check}\"|socat TCP4:localhost:3456 -"
        # ret = execute_command_with_polling(command_check)
        while not os.path.isfile(f"/socat-share/{command_id}.txt"):
            time.sleep(0.5)
        with open(f"/socat-share/{command_id}.txt","rb") as fs:
            print(fs.read().decode())
        os.remove(f"/socat-share/{command_id}.txt")
        return ret

    def ping(self):
        ret,error =execute_command_with_polling("echo 'echo ok'|socat TCP4:localhost:3456 -")
        return ret,error





