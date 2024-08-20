from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cyx/common/file_cacher.py',
		r'cyx/common/cacher.py',
		r'cyx/common/file_storage_disk.py',
		r'cyx/common/es_utils.py',
		r'cyx/common/base.py',
		r'cyx/common/audio_utils.py',
		r'cyx/common/basic_auth.py',
		r'cyx/common/share_storage.py',
		r'cyx/common/vn_text_normalizer.py',
		r'cyx/common/msg.py',
		r'cyx/common/file_information.py',
		r'cyx/common/rabitmq_message.py',
		r'cyx/common/content_marterial_utils.py',
		r'cyx/common/jwt_utils.py',
		r'cyx/common/test.py',
		r'cyx/common/file_storage.py',
		r'cyx/common/db_repository_services.py',
		r'cyx/common/mongo_db_services.py',
		r'cyx/common/file_storage_mongodb.py',
		r'cyx/common/temp_file.py',
		r'cyx/common/global_settings_services.py',
		r'cyx/common/msg_mongodb.py',
		r'cyx/common/brokers.py'],language_level = '3')
)
