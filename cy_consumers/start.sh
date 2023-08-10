#!/bin/bash
export APP_DIR=/home/vmadmin/python/v6/file-service-02
export PYTHON_ENV=/home/vmadmin/python/v6/file-service-02/venv-docker-003/bin/activate
echo $PYTHON_ENV
set -e
source $PYTHON_ENV
cd $APP_DIR/cy_consumers
python files_upload.py & \
python files_generate_thumbs.py & \
python files_extrac_text_from_image.py & \
python files_generate_image_from_office.py & \
python files_generate_image_from_pdf.py & \
python files_generate_image_from_video.py & \
#python files_generate_pdf_from_image.py & \
#python files_ocr_pdf.py & \
python files_save_custom_thumb.py & \
python files_save_default_thumb.py  & \
#python files_save_orc_pdf_file.py   & \
python files_save_search_engine.py



