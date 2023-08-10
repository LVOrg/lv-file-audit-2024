import pathlib
import subprocess
import sys
import os
working_dir = pathlib.Path(__file__).parent.__str__()
import os.path
import sys
import pathlib
import cython


sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
if sys.version_info.major ==3:
    print(sys.version)
else:
    raise Exception(f"incorect version. Current version is {sys.version}")
# if not cython.__version__.startswith("3."):
#     raise Exception(f"incorect cython version. Current version is {cython.__version__}")
def get_content_with_files(files, module_name):
    file_paths = "".join([f"\t\tr'{x}',\n" for x in files])
    file_paths=file_paths.rstrip('\n,').lstrip('\t')
    name = f"{module_name}"
    r = f"" \
        f"from setuptools import setup\n" \
        f"from Cython.Build import cythonize\n" \
        f"setup(\n" \
        f"\text_modules=cythonize([{file_paths}],language_level = '3')\n" \
        f")\n"
    return r
def get_content(file_path:str,package_name:str):
    file_name = pathlib.Path(file_path).name
    name  =f"{package_name}"
    r = f"" \
        f"from setuptools import setup\n" \
        f"from Cython.Build import cythonize\n" \
        f"setup(\n" \
        f"ext_modules=cythonize([r'{file_path}'],language_level = '3'),\n" \
        f")\n"
    return r


def generate_setup_file(full_gen_file, rel_dir):
    content = get_content(full_gen_file,rel_dir.replace(os.path.sep,'.').lstrip('.').rstrip('.'))
    if os.path.exists(full_gen_file):
        os.remove(full_gen_file)
    with open(full_gen_file,"w+") as f:
        f.write(content)

def get_list_of_file(full_compiler_dir):
    ret = []
    global working_dir
    root_dir, dirs, files = list(os.walk(full_compiler_dir))[0]


    for file in files:

        if pathlib.Path(file).name=="__init__.py":
            continue
        ret += [os.path.join(root_dir,file)]
    for dif in dirs:
        full_dir = os.path.join(root_dir, dif)
        fx = get_list_of_file(full_dir)
        ret += fx
    return ret

def generate_setup_file_files(ouput_dir, module_name, content):
    global working_dir
    full_out_dir = os.path.join(working_dir,ouput_dir)
    os.makedirs(full_out_dir,exist_ok=True)

    full_gen_file = os.path.join(full_out_dir,f"{module_name}_setup.py")
    if os.path.exists(full_gen_file):
        os.remove(full_gen_file)
    with open(full_gen_file, "w+") as f:
        f.write(content)
    return full_gen_file

def generate_compile_file(dir:str=None):
    ret = []
    global working_dir
    root_dir, dirs, files = list(os.walk(dir))[0]

    tem_dir_compile = os.path.join(working_dir,"cython-compile-temp")
    os.makedirs(tem_dir_compile,exist_ok=True)
    rel_dir = dir[len(working_dir):]

    for file in files:
        if os.path.splitext(file)[1]!=".py":
            continue
        if rel_dir == "":
            gen_file = file
        else:
            gen_file = ".".join([rel_dir.replace(os.path.sep,"."),file]).lstrip('.')
        full_gen_file = os.path.join(tem_dir_compile,gen_file)
        print(f"Generate file {full_gen_file} ...")

        print(f"Generate file {full_gen_file} is complete")
        ret+=[full_gen_file]
    for dif in dirs:
        full_dir = os.path.join(root_dir,dif)
        fx = generate_compile_file(full_dir)
        ret+=fx
    return ret


full_compiler_dir = sys.argv[1]
is_clear = False
is_dev = False
is_publish =False
if len(sys.argv)>2 and 'clear' in sys.argv:
    is_clear =True
if len(sys.argv) > 2 and 'dev' in sys.argv:
    is_dev = True
if len(sys.argv) > 2 and 'publish' in sys.argv:
    is_publish = True
    #python cy_es/setup.py build_ext --inplace
    #test/models
# list_of_files = generate_compile_file(full_compiler_dir)


list_of_files  = get_list_of_file(full_compiler_dir)
python_files = [x for x in list_of_files if os.path.splitext(x)[1] =='.py']
c_so_files = [x for x in list_of_files if os.path.splitext(x)[1] in ['.c','.so']]
c_files_only = [x for x in list_of_files if os.path.splitext(x)[1] == '.c']
if not is_dev:
    for x in c_so_files:
        os.remove(x)
        print(f"{x} was delete")
# os.chdir(working_dir)
if is_clear:
    print("all temp files was clear ")
    exit(0)

module_name = pathlib.Path(full_compiler_dir).name


content = get_content_with_files(files =python_files,module_name=module_name)





full_file = generate_setup_file_files(ouput_dir ="c-setup-tem", module_name = module_name,content = content)
print(full_file)

cmd = [
     sys.executable,full_file,
    'build_ext','--inplace']
command_line  = " ".join(cmd)
print(" ".join(cmd))
# subprocess.Popen(cmd_compile, cwd=root_dir)
# subprocess.call(command_line)
# ret = subprocess.check_output(cmd)
ret = subprocess.run(cmd)

#python cy_es/setup.py build_ext --inplace
list_of_files  = get_list_of_file(full_compiler_dir)
c_files_only = [x for x in list_of_files if os.path.splitext(x)[1] == '.c']
print("compiler is completed")
if not is_dev:
    for x in c_files_only:
        os.remove(x)
if is_publish:
    for x in python_files:
        os.remove(x)
