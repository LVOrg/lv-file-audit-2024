import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_es

if cy_es.cy_es_x.version()!='0.0.9.so':
    raise Exception(f"Incorrect version of cy_es., current version is {cy_es.cy_es_x.version()}")
else:
    print(cy_es.cy_es_x.version())

