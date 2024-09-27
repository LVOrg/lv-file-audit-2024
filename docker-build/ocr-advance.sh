#!/bin/bash
source build-func.sh
image_name="fs"
rm -f web-api-core
#nttlong/file-svc
#repository="docker.io/nttlong"
#repository="docker.lacviet.vn/xdoc"
if [ -z "$1" ]; then
  # No argument provided, use default repository
  repository="docker.io/nttlong"
else
  # Argument provided, use it as the repository
  repository="$1"
fi
if [ -z "$2" ]; then
  # No argument provided, use default repository
  customer="saas"
else
  # Argument provided, use it as the repository
  customer="$2"
fi
user="nttlong/file-svc"
platform=linux/amd64
ocr_advance_file="ocr-advance"

rm -f $ocr_advance_file
echo "
FROM myluke/ppocr:latest
RUN python3.7 -m pip install --upgrade pip
COPY ./../a-working/nvidia_cuda_nvrtc_cu11-11.7.99-2-py3-none-manylinux1_x86_64.whl /app/a-working/nvidia_cuda_nvrtc_cu11-11.7.99-2-py3-none-manylinux1_x86_64.whl
COPY ./../a-working/nvidia_cublas_cu11-11.10.3.66-py3-none-manylinux1_x86_64.whl /app/a-working/nvidia_cublas_cu11-11.10.3.66-py3-none-manylinux1_x86_64.whl
COPY ./../a-working/torch-1.13.1-cp37-cp37m-manylinux1_x86_64.whl /app/a-working/torch-1.13.1-cp37-cp37m-manylinux1_x86_64.whl
COPY ./../a-working/torchvision-0.14.1-cp37-cp37m-manylinux1_x86_64.whl /app/a-working/torchvision-0.14.1-cp37-cp37m-manylinux1_x86_64.whl
RUN pip install /app/a-working/nvidia_cuda_nvrtc_cu11-11.7.99-2-py3-none-manylinux1_x86_64.whl
RUN pip install /app/a-working/nvidia_cublas_cu11-11.10.3.66-py3-none-manylinux1_x86_64.whl
COPY ./../a-working/nvidia_cudnn_cu11-8.5.0.96-2-py3-none-manylinux1_x86_64.whl /app/a-working/nvidia_cudnn_cu11-8.5.0.96-2-py3-none-manylinux1_x86_64.whl
RUN pip install /app/a-working/nvidia_cudnn_cu11-8.5.0.96-2-py3-none-manylinux1_x86_64.whl
RUN pip install /app/a-working/torch-1.13.1-cp37-cp37m-manylinux1_x86_64.whl
RUN pip install /app/a-working/torchvision-0.14.1-cp37-cp37m-manylinux1_x86_64.whl
RUN pip install vietocr
COPY ./../py-torch /app/py-torch
RUN rm -fr /app/a-working
RUN apt clean && apt autoclean
">>$ocr_advance_file
ocr_advance_tag=2
ocr_core_tag_build="paddle-viet-ocr":$ocr_advance_tag
ocr_core_tag_image="docker.io/nttlong/"$ocr_core_tag_build
buildFunc $ocr_advance_file "docker.io/nttlong" "paddle-viet-ocr" $ocr_advance_tag "python:3.11.10-slim-bullseye" "alpine"
#docker pull nttlong/paddle-viet-ocr:$ocr_advance_tag
#docker tag nttlong/paddle-viet-ocr:$ocr_advance_tag docker.lacviet.vn/xdoc/paddle-viet-ocr:$ocr_advance_tag
#docker push docker.lacviet.vn/xdoc/paddle-viet-ocr:$ocr_advance_tag

ocr_advance_file_core="ocr-advance-core"
rm -f $ocr_advance_file_core
echo "
FROM docker.lacviet.vn/xdoc/paddle-viet-ocr:$ocr_advance_tag
COPY ./../docker-build/requirements/paddle-ocr.txt /app/docker-build/requirements/paddle-ocr.txt
RUN pip install -r /app/docker-build/requirements/paddle-ocr.txt
RUN apt clean && apt autoclean
">>$ocr_advance_file_core
ocr_advance_file_core_tag=$ocr_advance_tag.1
buildFunc $ocr_advance_file_core "docker.io/nttlong" "paddle-viet-ocr-core" $ocr_advance_file_core_tag "python:3.11.10-slim-bullseye" "alpine"

#docker pull nttlong/paddle-viet-ocr-core:$ocr_advance_file_core_tag
#docker tag nttlong/paddle-viet-ocr-core:$ocr_advance_file_core_tag docker.lacviet.vn/xdoc/paddle-viet-ocr-core:$ocr_advance_file_core_tag
#docker push docker.lacviet.vn/xdoc/paddle-viet-ocr-core:$ocr_advance_file_core_tag

action_ocr="action-viet-ocr"
rm -f $action_ocr
echo "
#FROM debian:unstable-slim
FROM docker.lacviet.vn/xdoc/paddle-viet-ocr-core:$ocr_advance_file_core_tag
COPY ./../docker-build/requirements/paddle-ocr.txt /app/docker-build/requirements/paddle-ocr.txt
RUN pip install -r /app/docker-build/requirements/paddle-ocr.txt
COPY ./../cy_file_cryptor /app/cy_file_cryptor
COPY ./../cy_docs /app/cy_docs
COPY ./../cy_es /app/cy_es
COPY ./../cy_kit /app/cy_kit
COPY ./../cy_logger /app/cy_logger
COPY ./../gridfs /app/gridfs
COPY ./../elasticsearch /app/elasticsearch
COPY ./../pymongo /app/pymongo
COPY ./../bson /app/bson
COPY ./../config.yml /app/config.yml
COPY ./../cy_controllers /app/cy_controllers
COPY ./../cy_services /app/cy_services
COPY ./../cy_ui /app/cy_ui
COPY ./../cy_utils /app/cy_utils
RUN rm -fr /app/cy_vn_suggestion/data
COPY ./../cy_web /app/cy_web
COPY ./../cy_xdoc /app/cy_xdoc
COPY ./../cy_plugins /app/cy_plugins
COPY ./../cyx /app/cyx
COPY ./../cy_consumers /app/cy_consumers
COPY ./../cy_jobs /app/cy_jobs
COPY ./../cy_libs /app/cy_libs
COPY ./../cy_lib_ocr /app/cy_lib_ocr
RUN apt clean && apt autoclean
#RUN pip install reportlab
">>$action_ocr
buildFunc $action_ocr "docker.lacviet.vn/xdoc" "composite-ocr" $ocr_advance_file_core_tag.18 "python:3.11.10-slim-bullseye" "alpine"
#docker run -it -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app docker.lacviet.vn/xdoc/composite-ocr:2.1.3 /bin/bash
#docker pull docker.lacviet.vn/xdoc/composite-ocr:$ocr_advance_file_core_tag.15
#docker tag docker.lacviet.vn/xdoc/composite-ocr:$ocr_advance_file_core_tag.14 nttlong/composite-ocr:$ocr_advance_file_core_tag.15
#docker push nttlong/composite-ocr:$ocr_advance_file_core_tag.14
