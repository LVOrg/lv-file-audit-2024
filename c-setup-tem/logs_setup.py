from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cy_controllers/logs/logs_controller.py'],language_level = '3')
)
