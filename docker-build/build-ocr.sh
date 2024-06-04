#!/bin/bash
#docker run -it  -v $(pwd)/../cy-commands:/cmd -v $(cms)/../tmp-files:/tmp-files -p 3456:3456  -v /socat-share:/socat-share --entrypoint /bin/bash  hdgigante/python-opencv:4.9.0-debian

source build-func.sh
image_name="fs"
rm -f build_file
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
build_file="ocr-processing"
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
rm -f $build_file
echo "
FROM python:3.10.13-bullseye
COPY ./../venv-remote-ocr/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./../hf /mnt/files/__dataset__/hf
ENV HUGGINGFACE_HUB_CACHE=/mnt/files/__dataset__/hf

RUN apt clean && apt autoclean
ENTRYPOINT [\"surya_gui\"]
">>$build_file
ocr_core_tag=1
#/home/vmadmin/python/cy-py/hf
#sudo mount -t nfs 192.168.18.36:/codx-file-storage/files/__dataset__/hf /home/vmadmin/python/cy-py/hf
#ocr_core_image="$repository/fs:"$ocr_core_tag_build
buildFunc $build_file $repository "surya-ocr" $ocr_core_tag "python:3.10-alpine" "alpine"
echo "docker run -p 1112:1112  -v /socat-share:/socat-share $repository/$image_name:$ocr_core_tag_build"

build_ocr_file="surya-ocr-entrypoint"
mr -f $build_ocr_file
echo "
FROM nttlong/surya-ocr:$ocr_core_tag
COPY ./../venv-remote-ocr/bin /usr/local/bin
ENV HUGGINGFACE_HUB_CACHE=/mnt/files/__dataset__/hf
RUN apt clean && apt autoclean
ENTRYPOINT [\"surya_gui\"]
">>$build_ocr_file
ocr_tag=$ocr_core_tag.1
#/home/vmadmin/python/cy-py/hf
#sudo mount -t nfs 192.168.18.36:/codx-file-storage/files/__dataset__/hf /home/vmadmin/python/cy-py/hf
#ocr_core_image="$repository/fs:"$ocr_core_tag_build
buildFunc $build_ocr_file $repository "surya-ocr-app" $ocr_core_tag "python:3.10-alpine" "alpine"
echo "docker run -p 1112:1112  -v /socat-share:/socat-share $repository/$image_name:$ocr_core_tag_build"