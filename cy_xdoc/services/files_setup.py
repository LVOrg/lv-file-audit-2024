import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()

file_path=os.path.join(build_dir, f"files.py")


setup(
    name='files_services',
    ext_modules=cythonize(file_path),
    zip_safe=True,
    packages=["files_services"]
)
#python cy_xdoc/services/files_setup.py build_ext --inplace
#python cy_web/setup.py bdist_wheel --universal