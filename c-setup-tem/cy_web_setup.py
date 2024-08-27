from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cy_web/standalone_application.py',
		r'cy_web/cy_web_x.py'],language_level = '3')
)
