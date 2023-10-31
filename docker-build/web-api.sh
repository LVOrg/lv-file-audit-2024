#!/bin/bash
source build-func.sh
image_name="fs"
rm -f web-api-core
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
web_api_core_file="web-api-core"

rm -f $web_api_core_file
echo "
FROM python:3.10-alpine
RUN apk add git
RUN pip install --upgrade pip
RUN python3 -m pip install git+https://github.com/Sudo-VP/Vietnamese-Word-Segmentation-Python.git
COPY ./../docker-build/requirements/web-api.req.txt /app/web-api.req.txt
RUN python3 -m pip install -r  /app/web-api.req.txt --no-cache-dir
">>$web_api_core_file
web_api_core_tag=2
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
RUN rm -fr /app/cy_vn_suggestion/data
COPY ./../cy_web /app/cy_web
COPY ./../cy_xdoc /app/cy_xdoc
COPY ./../cylibs /app/cylibs
COPY ./../cyx /app/cyx">>$web_api_file
web_api_tag=13
web_api_tag_build="api.apps."$(tag $web_api_core_tag).$web_api_tag
web_api_image=web:"apps".$web_api_core_tag_build
buildFunc $web_api_file $repository $image_name $web_api_tag_build "python:3.10-alpine" "alpine"
echo "in order to test:"
echo "docker run -v $(pwd)/..:/app -p 8012:8012 $repository/$image_name:$web_api_tag_build"