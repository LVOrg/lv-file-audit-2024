#!/bin/sh
echo "$PWD"
APP_DIR="/app"
rabbitmq_msg="test"
PYTHON_ENV=$APP_DIR/venv-docker-003/bin/activate
echo $PYTHON_ENV
python_run=$(which python3)
if [ -e "$PYTHON_ENV" ]; then
  ### Take action if $DIR exists ###
  python_run=$APP_DIR/venv-docker-003/bin/python
else
  python_run=$(which python3)
fi

##activate()
#python_run="$(which python3)"
server_dir=cy_xdoc
service_dir=cy_consumers
echo $python_run

$python_run $APP_DIR/$service_dir/files_upload.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_generate_thumbs.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_extrac_text_from_image.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_generate_image_from_office.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_generate_image_from_pdf.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_generate_image_from_video.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_generate_pdf_from_image.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_ocr_pdf.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_save_custom_thumb.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_save_default_thumb.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_save_orc_pdf_file.py   rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$service_dir/files_save_search_engine.py  rabbitmq.msg=$rabbitmq_msg & \
$python_run $APP_DIR/$server_dir/server.py rabbitmq.msg=$rabbitmq_msg
