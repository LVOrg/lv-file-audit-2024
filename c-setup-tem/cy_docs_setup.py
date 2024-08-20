from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cy_docs/cy_engine.py',
		r'cy_docs/cy_docs_x.py',
		r'cy_docs/cy_xdoc_utils.py'],language_level = '3')
)
