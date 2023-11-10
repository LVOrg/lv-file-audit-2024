#!/bin/bash
source build-func.sh
image_name="fs"
text_pdf_file_core="text_pdf_core"

#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64

du -sh $(pwd)/../env_text_from_pdf/lib/python3.10/site-packages/* | sort -h
rm -f text_pdf_file_core
echo "
FROM docker.io/python:3.10.12-slim-bookworm
COPY  ./../env_text_from_pdf/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
RUN   apt update && apt install python3-opencv -y
">>$text_pdf_file_core
text_pdf_file_core_tag=1
text_pdf_file_core_tag_build="job.apps.text.pdf.libs."$(tag $job_core_tag)
text_pdf_file_core_image=$repository/$image_name:$text_pdf_file_core_tag_build
buildFunc $text_pdf_file_core $repository $image_name $text_pdf_file_core_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"

echo "in order to check image run:"
echo "docker run -it -v \$(pwd)/..:/app nttlong/fs:$job_core_tag_build  /bin/bash"
echo "python3 /app/cy_consumers/files_upload.py"
echo "python3 /app/cy_consumers/files_generate_thumbs.py"
echo "python3 /app/cy_consumers/files_save_custom_thumb.py"
echo "python3 /app/cy_consumers/files_generate_pdf_from_image.py"
echo "python3 /app/cy_consumers/files_clean_up.py"
echo "python3 /app/cy_consumers/files_generate_image_from_pdf.py"
#docker run -it -v $(pwd):/app nttlong/fs:job.slim.libs.amd.1 /bin/bash
text_pdf_file="text_pdf_file"
echo "
FROM $text_pdf_file_core_image
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
COPY ./../cy_consumers /app/cy_consumers
COPY ./../cy_services /app/cy_services
COPY ./../cy_ui /app/cy_ui
COPY ./../cy_utils /app/cy_utils
COPY ./../cy_vn /app/cy_vn
COPY ./../cy_vn_suggestion /app/cy_vn_suggestion
COPY ./../cy_web /app/cy_web
COPY ./../cy_xdoc /app/cy_xdoc
COPY ./../cylibs /app/cylibs
COPY ./../cy_plugins /app/cy_plugins
COPY ./../cyx /app/cyx">>$text_pdf_file
text_pdf_file_tag=1
text_pdf_file_tag_build="job.apps.text.pdf."$(tag $text_pdf_file_core_tag).$text_pdf_file_tag
text_pdf_file_image=$repository/$image_name.$text_pdf_file_tag_build
buildFunc $text_pdf_file $repository $image_name $text_pdf_file_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"