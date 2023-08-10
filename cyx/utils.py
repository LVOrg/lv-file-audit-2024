def run_command(cmd: str) -> str:
    import subprocess
    import os
    output = subprocess.check_output(
        cmd.replace("  ", " ").split(" "),
        stderr=subprocess.STDOUT,
        env=os.environ,
        stdin=subprocess.DEVNULL,
    )
    txt_output = output.decode("utf-8").lstrip('\n').rstrip('\n')
    return txt_output


def easyocr_get_langs_suport():
    import easyocr
    import pathlib
    import os
    easyocr_dir = os.path.join(pathlib.Path(easyocr.__file__).parent.__str__(), "character")
    print(easyocr_dir)
    txt = run_command(f"find {easyocr_dir} -name *_char.txt")
    print()
    items = txt.split('\n')
    items = [pathlib.Path(x).stem for x in items]
    items = [x[:-len("_char")] for x in items]
    return items
#curl -X PUT localhost:9200/_cluster/settings -H "Content-Type: application/json" -d '{ "persistent": { "cluster.max_shards_per_node": "3000" } }'
