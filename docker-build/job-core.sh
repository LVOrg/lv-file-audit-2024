#!/bin/bash
source build-func.sh
image_name="fs"
job_core_file="job-core"

#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64


rm -f $job_core_file
echo "
FROM docker.io/python:3.10.12-slim-bookworm
RUN apt update -y
RUN pip install --upgrade pip
RUN apt install git -y
COPY ./../docker-cy/requirements/job-services.txt /app/job-services.txt
RUN python3 -m pip install -r  /app/job-services.txt
">>$job_core_file
web_api_core_tag=1
web_api_core_tag_build="api.libs."$(tag $web_api_core_tag)
web_api_core_image="$repository/fs:"$web_api_core_tag_build
buildFunc $web_api_core_file $repository $image_name $web_api_core_tag_build "python:3.10-alpine" "alpine"
web_api_file="web-api"
rm -f $web_api_file

echo "ARG BASE
FROM $web_api_core_image
ARG TARGETARCH
ARG OS
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
COPY ./../cy_vn /app/cy_vn
COPY ./../cy_vn_suggestion /app/cy_vn_suggestion
COPY ./../cy_web /app/cy_web
COPY ./../cy_xdoc /app/cy_xdoc
COPY ./../cylibs /app/cylibs
COPY ./../cyx /app/cyx">>$web_api_file
web_api_tag=3
web_api_tag_build="api.apps."$(tag $web_api_core_tag).$web_api_tag
web_api_image=web:"apps".$web_api_core_tag_build
buildFunc $web_api_file $repository $image_name $web_api_tag_build "python:3.10-alpine" "alpine"