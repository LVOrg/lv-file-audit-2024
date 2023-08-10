print("Install deep-learning dataset")
import shutil
import shutil
import os

original = f"/tmp/data/dataset"
target = r'/app/dataset'


def move_files(source, dest):
    print(f"move:\n \t{source} \n\t {target}")
    root, dir_names, file_names = list(os.walk(source))[0]
    for file_name in file_names:
        source_file = os.path.abspath(os.path.join(source,file_name))
        dest_file = os.path.abspath(os.path.join(dest, file_name))
        try:
            if not os.path.isfile(dest_file):
                shutil.copy(source_file,dest_file)
        except Exception as e:
            print(e)



    for dir_name in dir_names:
        dest_dir = os.path.abspath(os.path.join(dest, dir_name))
        source_dir = os.path.abspath(os.path.join(source, dir_name))
        try:
            os.makedirs(dest_dir, exist_ok=True)
            move_files(source_dir,dest_dir)
        except Exception as e:
            print(e)



move_files(original,target)
print("Finish")


