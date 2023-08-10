print("Check tika server")

try:
    import pathlib

    working_path = pathlib.Path(__file__).parent.__str__()
    import sys
    import os

    sys.path.append(working_path)
    ext_lib_folder = os.path.abspath(os.path.join(working_path))
    path_to_java = os.path.join(ext_lib_folder, "tika-server.jar")
    path_to_java_md5 = os.path.join(ext_lib_folder, "tika-server.jar.md5")
    if not os.path.isfile(path_to_java):
        raise Exception(f"f{path_to_java} was not found")
    if not os.path.isfile(path_to_java_md5):
        raise Exception(f"f{path_to_java_md5} was not found")
    if not os.path.isdir(ext_lib_folder):
        raise Exception(f"f{ext_lib_folder} was not found")
    import subprocess

    ret = subprocess.check_output(["which", "java"])
    ret_ttx = ret.decode('utf8')
    java_path = ret_ttx.lstrip('\n').rstrip('\n')
    if not os.path.isfile(java_path):
        raise Exception("java was not found")
    subprocess.Popen(java_path, stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
    # os.environ['TIKA_JAVA']=ret_ttx
    os.environ['TIKA_SERVER_JAR'] = path_to_java
    os.environ['TIKA_PATH'] = ext_lib_folder
    os.environ['TIKA_STARTUP_SLEEP'] = '10'
    os.environ['TIKA_STARTUP_MAX_RETRY'] = '10'

    # os.environ['TIKA_CLIENT_ONLY']='true'
    # os.environ['TIKA_SERVER_ENDPOINT']='http://172.16.13.72:9998'
    if sys.modules.get("tika") is not None:
        import importlib

        importlib.reload(sys.modules["tika"])

    import tika
    from tika import tika as tk

    tk.TikaJava
    try:
        tika.initVM()
        from tika import parser

        headers = {

        }
        ret = parser.from_file(__file__)  # ,  requestOptions={'headers': headers, 'timeout': 3000000})
        print(ret)
        print("Check tika server is ok")
    except Exception as e:
        raise Exception("Init tika server fail")
except Exception as e:
    raise e
