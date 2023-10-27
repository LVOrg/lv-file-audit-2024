import pathlib
import sys


working_dir = pathlib.Path(__file__).parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
from cy_grpc.serverless import start_serverles
def handler(data:dict,context)->dict:
    print(data)
    try:
        data["test"] =  1
        return dict(
            data=data
        )
    except Exception as e:
        return  dict(
            error=str(e)
        )
start_serverles(50011,handler)
