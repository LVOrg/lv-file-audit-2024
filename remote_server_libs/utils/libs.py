import subprocess
import time
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
            try:
                line = process.stdout.readline().decode()
                print(line)
            except Exception as ex:
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
    except Exception as ex:
        raise ex