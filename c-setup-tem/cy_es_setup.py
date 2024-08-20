from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cy_es/cy_es_utils.py',
		r'cy_es/cy_es_data_parser.py',
		r'cy_es/cyx_es_delete.py',
		r'cy_es/cy_es_manager.py',
		r'cy_es/cy_es_docs.py',
		r'cy_es/cy_es_objective.py',
		r'cy_es/cy_es_json.py'],language_level = '3')
)
