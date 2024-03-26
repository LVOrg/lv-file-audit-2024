import subprocess
import time


class OSCommandService:
    def __init__(self):
        pass

    def execute_command_with_polling(self, commands):
        """
      Executes a command line and prints output while it's running.

      Args:
          command: A string representing the command to execute.
      """

        process = subprocess.Popen(" ".join(commands), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while process.poll() is None:
            # Check for new output periodically (adjust interval as needed)
            try:
                line = process.stdout.readline().decode()
                if line:
                    print(line, end='')  # Print without newline to avoid extra line breaks

            except:
                continue
            time.sleep(0.1)  # Adjust sleep time for desired polling frequency

        # Wait for the command to finish and get the final output
        output, error = process.communicate()
        if error:
            return error.decode()
        else:
            return output.decode()
