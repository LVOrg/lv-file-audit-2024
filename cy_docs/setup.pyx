import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
file=os.path.join(pathlib.Path(__file__).parent.__str__(), f"cy_docs_x.py")
print(file)
setup(
    name='cy_docs',
    ext_modules=cythonize(file,language_level = "3"),
    zip_safe=True,
    packages=["cy_docs"]
)
#python cy_docs/setup.py build_ext --inplace