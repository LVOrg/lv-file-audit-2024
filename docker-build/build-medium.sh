#!/bin/bash
rm -f office-core
echo "
FROM linuxserver/libreoffice
RUN apk add py3-pip
RUN apk add git
RUN python3 -m pip install moviepy
RUN python3 -m pip install python-memcached
RUN python3 -m pip install passlib
RUN python3 -m pip install humanize
RUN python3 -m pip install uvicorn
RUN python3 -m pip install python-jose
RUN python3 -m pip install git+https://github.com/Sudo-VP/Vietnamese-Word-Segmentation-Python.git
RUN python3 -m pip install tika
RUN python3 -m pip install pdfplumber
RUN python3 -m pip install PyPDF2
RUN python3 -m pip install img2pdf
RUN python3 -m pip install grpcio
RUN python3 -m pip install grpcio-tools
RUN python3 -m pip install slackclient
RUN python3 -m pip install python-onedrive
RUN python3 -m pip install microsoftgraph-python
RUN python3 -m pip install msal
#COPY ./../docker-cy/templates/office.req.txt /app/office.req.txt
#RUN python3 -m pip install -r /app/office.req.txt
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
FROM python:3.10.12-slim-bookworm
RUN apt update
RUN apt-get upgrade -y
RUN apt install libreoffice -y
#RUN apt-get update --fix-missing
#RUN apt install libreoffice -y
RUN apt install git -y
#RUN apk update && apk upgrade
#RUN apk add py3-pip
#RUN apk --no-cache update && apk add --no-cache python3 py3-pip
#RUN apk add git
#RUN apk add --no-cache py3-pip
#RUN apk add py3-pip
#RUN apk add git
#RUN apt-get install -y build-essential python3-dev
#COPY ./../docker-build/requirements/office.req.txt /app/office.req.txt
#RUN apk add --no-cache python3
#RUN python3 -m pip install fastapi
#RUN python3 -m pip install -r /app/office.req.txt --no-cache-dir
#ENTRYPOINT [\"/usr/bin/env\"]
#COPY ./../env_office/lib/python3.11/site-packages /usr/local/lib/python3.11/dist-packages
RUN apt clean && apt autoclean
">>$job_core_office_file
job_core_office_tag=14
job_core_office_build="fs.medium.core."$(tag $job_core_office_tag)
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
COPY ./../docker-build/requirements/office.req.txt /app/requirements/office.req.txt
RUN python3 -m pip install -r /app/requirements/office.req.txt --no-cache-dir
#COPY ./../env_libre_office/lib/python3.10/site-packages /usr/local/lib/python3.10/dist-packages
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
COPY ./../cy_fucking_whore_microsoft /app/cy_fucking_whore_microsoft
COPY ./../cyx /app/cyx">>$job_office_file
job_office_tag=2
job_office_tag_build="fs.medium."$(tag $job_core_office_tag).$job_office_tag
job_office_image=$repository/$image_name.$job_office_tag_build
buildFunc $job_office_file $repository $image_name $job_office_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
#soffice --headless --convert-to pdf test-002.docx --outdir split_files-003
#soffice --headless --convert-to pdf:calc_pdf_Export    test-001.xlsx --outdir split_files-008
#qpdf --split-pages=1 test-002.pdf output-page-%d.pdf
#soffice --headless --extract-pages test.docx --outdir split_files --single-page
#docker run -it --entrypoint bash -v $(pwd)/../a-working:/tmp/test plamapp2one/docker-unoconv-webservice:latest
#docker run -it --entrypoint bash -v $(pwd)/../a-working:/tmp/test linuxserver/libreoffice
#docker run -it --entrypoint bash norem/unoconverter:latest
#unoconv -f pdf -e PageRange=1-3 test.doc
#https://vmiklos.hu/blog/pdf-convert-to.html
