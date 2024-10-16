from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cy_file_cryptor/google_drive_download.py',
		r'cy_file_cryptor/modifier_buffered_writer.py',
		r'cy_file_cryptor/reader_chunks.py',
		r'cy_file_cryptor/mongodb_file.py',
		r'cy_file_cryptor/httpio.py',
		r'cy_file_cryptor/writer_text.py',
		r'cy_file_cryptor/google_drive_upload.py',
		r'cy_file_cryptor/remote_file.py',
		r'cy_file_cryptor/settings.py',
		r'cy_file_cryptor/crypt_info.py',
		r'cy_file_cryptor/context.py',
		r'cy_file_cryptor/writer_binary_v02.py',
		r'cy_file_cryptor/reader_binary.py',
		r'cy_file_cryptor/cy_to_thread.py',
		r'cy_file_cryptor/wrappers.py',
		r'cy_file_cryptor/encrypting.py',
		r'cy_file_cryptor/modifier_buffered_reader.py',
		r'cy_file_cryptor/writer_binary.py',
		r'cy_file_cryptor/writer_binary_comit_v02.py',
		r'cy_file_cryptor/reader_binary_v02.py',
		r'cy_file_cryptor/reader_text.py',
		r'cy_file_cryptor/security_context.py',
		r'cy_file_cryptor/utf8_encrypting.py',
		r'cy_file_cryptor/modifier_text_io_wrapper.py',
		r'cy_file_cryptor/remote_file_io.py',
		r'cy_file_cryptor/google_drive_stream.py'],language_level = '3')
)
