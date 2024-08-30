from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'a_checking/long_test/test_func.py'],language_level = '3')
)
