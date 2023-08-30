import pathlib
import sys


def get_cwd()->str:
    return pathlib.Path(__file__).parent.parent.__str__()
def init_env():
    sys.path.append(get_cwd())

init_env()