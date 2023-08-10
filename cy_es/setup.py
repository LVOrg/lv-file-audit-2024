import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()

file_path=os.path.join(build_dir, f"cy_es_x.py")


setup(
    name='cy_es_x',
    ext_modules=cythonize(file_path,language_level = "3"),
    zip_safe=True,
    packages=["cy_es_x"]
)
#python cy_es/setup.py build_ext --inplace