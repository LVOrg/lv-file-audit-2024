#!/bin/bash
echo "
FROM linuxserver/libreoffice
RUN apk add py3-pip git
COPY ./../docker-cy/templates/office.req.txt /app/office.req.txt
RUN python3 -m pip install -r /app/office.req.txt
ENTRYPOINT [\"/usr/bin/env\"]
">>office-core

#!/bin/bash
source build-func.sh
image_name="fs"
job_core_office_file="job-core-office"

#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
rm -f $job_core_office_file
echo "
FROM linuxserver/libreoffice
RUN apk add py3-pip git
COPY ./../docker-build/requirements/office.req.txt /app/office.req.txt
RUN python3 -m pip install -r /app/office.req.txt --no-cache-dir
ENTRYPOINT [\"/usr/bin/env\"]
">>$job_core_office_file
job_core_office_tag=2
job_core_office_build="job.office.libs."$(tag $job_core_office_tag)
job_core_office_image=$repository/$image_name:$job_core_office_build
buildFunc $job_core_office_file $repository $image_name $job_core_office_build "docker.io/python:3.10.12-slim-bookworm" "debian"
#mount -t nfs 172.16.13.72:/home/vmadmin/python/cy-py //from-172-16-13-72-cy-py
echo "in order to check image run:"
echo "docker run -it -v \$(pwd)/..:/app nttlong/fs:$job_core_office_build  /bin/bash"
echo "python3 /app/cy_consumers/files_upload.py"
echo "python3 /app/cy_consumers/files_generate_thumbs.py"
echo "python3 /app/cy_consumers/files_save_custom_thumb.py"
echo "python3 /app/cy_consumers/files_generate_pdf_from_image.py"
echo "python3 /app/cy_consumers/files_clean_up.py"
echo "python3 /app/cy_consumers/files_generate_image_from_pdf.py"
#docker run -it -v $(pwd):/app nttlong/fs:job.slim.libs.amd.1 /bin/bash
job_office_file="job-office-file"
rm -fr $job_office_file
echo "
FROM $job_core_office_image
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
COPY ./../cyx /app/cyx">>$job_office_file
job_office_tag=3
job_office_tag_build="job.office."$(tag $job_core_office_tag).$job_office_tag
job_office_image=$repository/$image_name.$job_office_tag_build
buildFunc $job_office_file $repository $image_name $job_office_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"