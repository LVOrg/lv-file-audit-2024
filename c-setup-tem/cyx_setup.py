from setuptools import setup
from Cython.Build import cythonize
setup(
	ext_modules=cythonize([r'cyx/app_utils_services.py',
		r'cyx/extract_content_service.py',
		r'cyx/lv_upload_file.py',
		r'cyx/cloud_storage_sync_services.py',
		r'cyx/local_file_caching_services.py',
		r'cyx/logs_to_mongo_db_services.py',
		r'cyx/local_api_services.py',
		r'cyx/pdf_content_services.py',
		r'cyx/pdf_vietocr.py',
		r'cyx/easy_ocr.py',
		r'cyx/loggers.py',
		r'cyx/gemini_service.py',
		r'cyx/remote_caller.py',
		r'cyx/repository.py',
		r'cyx/file_utils_services.py',
		r'cyx/elastic_search_utils_service.py',
		r'cyx/content_manager_services.py',
		r'cyx/base.py',
		r'cyx/socat_services.py',
		r'cyx/file_content_process.py',
		r'cyx/cloud_cache_services.py',
		r'cyx/docs_contents_services.py',
		r'cyx/rabbit_utils.py',
		r'cyx/file_utils_services_base.py',
		r'cyx/files_paths.py',
		r'cyx/test_spacy.py',
		r'cyx/log_watcher_service.py',
		r'cyx/file_sync.py',
		r'cyx/test.py',
		r'cyx/check.py',
		r'cyx/linguistics.py',
		r'cyx/check_start_up.py',
		r'cyx/files_reader.py',
		r'cyx/runtime_config_services.py',
		r'cyx/os_command_services.py',
		r'cyx/file_process_mapping.py',
		r'cyx/content_services.py',
		r'cyx/lv_ocr_services.py',
		r'cyx/images.py',
		r'cyx/fix_miss_thumbs.py',
		r'cyx/utils.py',
		r'cyx/fix_es.py',
		r'cyx/thumbs_services.py',
		r'cyx/files_converter.py',
		r'cyx/malloc_services.py',
		r'cyx/image_services.py',
		r'cyx/g_drive_services.py',
		r'cyx/processing_file_manager_services.py',
		r'cyx/dd2/check.py',
		r'cyx/dd2/utils.py',
		r'cyx/vn_predictor_delete/predictor.py',
		r'cyx/token_manager/request_service.py',
		r'cyx/token_manager/token_service.py',
		r'cyx/audio/audio_service.py',
		r'cyx/ext_libs/vn_validator.py',
		r'cyx/ext_libs/cy_utils.py',
		r'cyx/ext_libs/check.py',
		r'cyx/ext_libs/vn_dict_build.py',
		r'cyx/ext_libs/vn_word_analyzer.py',
		r'cyx/ext_libs/vn_predicts.py',
		r'cyx/ext_libs/vn_corrector.py',
		r'cyx/ocr_vietocr_utils/check.py',
		r'cyx/ocr_vietocr_utils/ocr_content.py',
		r'cyx/google_drive_utils/directories.py',
		r'cyx/remote_libs/office_services.py',
		r'cyx/remote_libs/check.py',
		r'cyx/db_models/users.py',
		r'cyx/db_models/sso.py',
		r'cyx/db_models/errors.py',
		r'cyx/db_models/apps.py',
		r'cyx/db_models/files.py',
		r'cyx/common/file_cacher.py',
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
		r'cyx/common/brokers.py',
		r'cyx/cloud/mail_service_google.py',
		r'cyx/cloud/cloud_file_sync_service.py',
		r'cyx/cloud/cloud_file_sync_service_azure.py',
		r'cyx/cloud/drive_services.py',
		r'cyx/cloud/cloud_upload_google_service.py',
		r'cyx/cloud/cloud_upload_azure_service.py',
		r'cyx/cloud/drive_service_google.py',
		r'cyx/cloud/mail_service_ms.py',
		r'cyx/cloud/drive_service_ms.py',
		r'cyx/cloud/cloud_file_sync_service_google.py',
		r'cyx/cloud/google_utils.py',
		r'cyx/cloud/cloud_service_utils.py',
		r'cyx/cloud/mail_services.py',
		r'cyx/cloud/azure/office365_services.py',
		r'cyx/cloud/azure/azure_utils.py',
		r'cyx/cloud/azure/azure_utils_services.py',
		r'cyx/cloud/azure/cy_wopi/models.py',
		r'cyx/cloud/azure/cy_wopi/wopi_request_process.py',
		r'cyx/cloud/azure/cy_wopi/wopi_request_headers.py',
		r'cyx/cloud/azure/cy_wopi/wopi_discovery.py',
		r'cyx/cloud/azure/cy_wopi/wopi_url_placeholders.py',
		r'cyx/cloud/azure/cy_wopi/check.py',
		r'cyx/cloud/azure/cy_wopi/utils.py',
		r'cyx/cloud/azure/cy_wopi/wopi_request.py',
		r'cyx/cloud/azure/cy_wopi/wopi_response_headers.py',
		r'cyx/cloud/azure/cy_wopi/wopi_utils.py',
		r'cyx/graphic_utils/opencv_enhance.py',
		r'cyx/rdr_segmenter_delete/segmenter_services.py',
		r'cyx/media/video.py',
		r'cyx/media/exe.py',
		r'cyx/media/libre_office.py',
		r'cyx/media/image_extractor.py',
		r'cyx/media/contents.py',
		r'cyx/media/pdf.py',
		r'cyx/media/core/graphics.py',
		r'cyx/video/extract_text_from_video_service.py',
		r'cyx/video/video_services.py',
		r'cyx/tools/progress_bar.py',
		r'cyx/document_layout_analysis/system.py',
		r'cyx/document_layout_analysis/test_on_web.py',
		r'cyx/document_layout_analysis/test_table_ocr_console.py',
		r'cyx/document_layout_analysis/doctr_service.py',
		r'cyx/document_layout_analysis/table_ocr_service.py',
		r'cyx/db_services/error_services.py',
		r'cyx/cache_service/memcache_service.py',
		r'cyx/console/console_services.py',
		r'cyx/ms/ms_auth_services.py',
		r'cyx/ms/ms_commom_service.py'],language_level = '3')
)
