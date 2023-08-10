import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_es
check_version  = '0.0.9.so'
if cy_es.cy_es_x.version()!=check_version:
    raise Exception(f"Incorrect version of cy_es.cy_es_x.Desire {check_version} but current Version is {cy_es.cy_es_x.version()}\n"
                    f"Python path {sys.executable}")
else:
    print(cy_es.cy_es_x.version())