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
web_api_core_file="web-api-core"

rm -f $web_api_core_file
echo "
FROM python:3.10.13-bullseye
#RUN apt update
#RUN apt-get install git
#RUN pip install --upgrade pip
#RUN apt install socat -y
#RUN python3 -m pip install git+https://github.com/Sudo-VP/Vietnamese-Word-Segmentation-Python.git --no-cache-dir
#COPY ./../docker-build/requirements/web-api.req.txt /app/web-api.req.txt
#RUN python3 -m pip install -r  /app/web-api.req.txt --no-cache-dir
COPY ./../env_webapi/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
RUN apt clean && apt autoclean
">>$web_api_core_file
web_api_core_tag=22
web_api_core_tag_build="fs.tiny.core."$(tag $web_api_core_tag)
web_api_core_image="docker.io/nttlong/fs:"$web_api_core_tag_build
buildFunc $web_api_core_file "docker.io/nttlong" $image_name $web_api_core_tag_build "python:3.10-alpine" "alpine"
web_api_file="web-api"
rm -f $web_api_file
du -sh $(pwd)/../env_webapi/lib/python3.10/site-packages/* | sort -h
echo "ARG BASE
FROM $web_api_core_image
#FROM python:3.10.13-bullseye
ARG TARGETARCH
ARG OS
#COPY ./../env_webapi/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
ENV PRODUCTION_BUILT_ON=\"$(date +"%Y-%m-%d %H:%M:%S")\"
ENV BUILD_IMAGE_TAG=\"$web_api_core_tag_build\"
RUN python3 -m pip install webp
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
#COPY ./../cy_vn /app/cy_vn
#COPY ./../cy_vn_suggestion /app/cy_vn_suggestion
RUN rm -fr /app/cy_vn_suggestion/data
COPY ./../cy_web /app/cy_web
COPY ./../cy_xdoc /app/cy_xdoc
COPY ./../cylibs /app/cylibs
COPY ./../cy_plugins /app/cy_plugins
#COPY ./../cy_fw_microsoft_delete /app/cy_fw_microsoft_delete
COPY ./../cyx /app/cyx
COPY ./../cy_consumers /app/cy_consumers
COPY ./../cy_jobs /app/cy_jobs
#RUN python3 -m pip install gradio==3.50.2
#RUN python3 -m pip install gradio-client==0.15.1
RUN apt clean && apt autoclean">>$web_api_file
web_api_tag=1
current_datetime=$(date +"%Y-%-m-%d-%H-%M-%S")
filename="release-notes/$customer.txt"
echo "$current_datetime:">>"$filename"
if [ -z "$3" ]; then
  # No argument provided, use default repository
  web_api_tag_build=$web_api_core_tag.$current_datetime
else
  # Argument provided, use it as the repository
  web_api_tag_build=$web_api_tag
fi
web_api_tag_build=build-$web_api_core_tag.$current_datetime

web_api_image="fs-tiny":$web_api_core_tag_build
buildFunc $web_api_file $repository "fs-tiny-$customer" $web_api_tag_build "python:3.10-alpine" "alpine"
echo "in order to test:"
echo "docker run -v $(pwd)/..:/app -p 8012:8012 $repository/$image_name:$web_api_tag_build"
