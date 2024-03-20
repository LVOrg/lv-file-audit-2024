#!/bin/bash
source build-func.sh
repository="docker.io/nttlong"
platform=linux/amd64
image_name="fs"

ai_lib_file="ai-lib"
run rm -f $ai_lib_file
echo "
ARG BASE
FROM jbarlow83/ocrmypdf
ARG TARGETARCH
ARG OS
RUN apt-get update && apt-get install tesseract-ocr-vie
COPY ./../env_jobs/lib/python3.10/site-packages /usr/local/lib/python3.10/dist-packages
ENTRYPOINT []
">>$ai_lib_file
ai_lib_tag=11
ai_lib_tag_build="fs.large.core."$(tag $ai_lib_tag)
ai_lib_image=$repository/$image_name.$ai_lib_tag_build
buildFunc $ai_lib_file $repository $image_name $ai_lib_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
echo "in order to check image run:"
echo "docker run -it -v \$(pwd)/..:/app --entrypoint bash nttlong/fs:$ai_lib_tag_build  /bin/bash"
echo "python3 /app/cy_consumers/files_ocr_pdf.py"
echo "python3 /app/cy_consumers/files_extrac_text_from_image.py"
ai_file="ai"
run rm -f $ai_file
echo "
ARG BASE
FROM nttlong/fs:$ai_lib_tag_build
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
COPY ./../docker-cy/templates/web-api.req.txt /app/web-api.req.txt
COPY ./../cy_services /app/cy_services
COPY ./../cy_ui /app/cy_ui
COPY ./../cy_utils /app/cy_utils
COPY ./../cy_vn /app/cy_vn
COPY ./../cy_vn_suggestion /app/cy_vn_suggestion
COPY ./../cy_web /app/cy_web
COPY ./../cy_xdoc /app/cy_xdoc
COPY ./../cylibs /app/cylibs
COPY ./../cyx /app/cyx
COPY ./../cy_consumers /app/cy_consumers
COPY ./../cy_plugins /app/cy_plugins
COPY ./../cy_fucking_whore_microsoft /app/cy_fucking_whore_microsoft
COPY ./../cy-dataset /app/cy-dataset
RUN apt clean && apt autoclean

ENTRYPOINT []
">>$ai_file
ai_tag=4
ai_tag_build="fs.large."$(tag $ai_lib_tag).$ai_tag
ai_image=$repository/$image_name:$ai_tag_build
buildFunc $ai_file $repository $image_name $ai_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
echo "in order to check image run:"
echo "docker run -it -v \$(pwd)/..:/app  $ai_image  /bin/bash"
echo "python3 /app/cy_consumers/files_ocr_pdf.py"
echo "python3 /app/cy_consumers/files_extrac_text_from_image.py"
