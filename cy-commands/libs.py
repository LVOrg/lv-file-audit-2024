import subprocess
import time
import requests


def download_file(url, download_to_file):
    """
    Downloads a file from the given URL to the specified location.

    Args:
        url (str): The URL of the file to download.
        download_location (str): The path to the directory where the file should be saved.

    Returns:
        None

    Raises:
        Exception: If any error occurs during the download process.
    """

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(download_to_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return download_to_file

    except Exception as e:
        print(f"An error occurred during download: {e}")


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
