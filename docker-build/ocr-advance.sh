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
docker pull nttlong/paddle-viet-ocr:$ocr_advance_tag
docker tag nttlong/paddle-viet-ocr:$ocr_advance_tag docker.lacviet.vn/xdoc/paddle-viet-ocr:$ocr_advance_tag
docker push docker.lacviet.vn/xdoc/paddle-viet-ocr:$ocr_advance_tag
