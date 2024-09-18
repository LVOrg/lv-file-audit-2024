from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'/root/python-2024/lv-file-fix-2024/py-files-sv/cy_libs/tmp_files_servcices.py'],language_level = '3')
)
