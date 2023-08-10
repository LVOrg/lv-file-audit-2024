import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_docs

if cy_docs.cy_docs_x.get_version()!='0.0.4.so':
    raise Exception(f"Incorrect version of cy_docs.cy_docs_x.version(). Version is {cy_docs.cy_docs_x.get_version()}")
else:
    print(cy_docs.cy_docs_x.get_version())