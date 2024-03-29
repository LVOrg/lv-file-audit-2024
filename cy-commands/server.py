import argparse
import pathlib
import atexit
import sys
import psutil
sys.path.append(pathlib.Path(__file__).parent.__str__())
import utils
import subprocess
if __name__ == '__main__':
    print("srat at 8765")
    pid = utils.get_pid_using_port(8765)
    if isinstance(pid,int):
        utils.kill_process(pid)
    def executor(cmd:str):
        print(f"receive command {cmd}")
        return utils.execute_command_with_polling(cmd)
    process,th = utils.socat_watcher(8765,executor)
    th.join(1)

    @atexit.register
    def goodbye():
        process.kill()
        print("GoodBye.")
