from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cyx/db_models/users.py',
		r'cyx/db_models/sso.py',
		r'cyx/db_models/errors.py',
		r'cyx/db_models/apps.py',
		r'cyx/db_models/files.py'],language_level = '3')
)
