#!/bin/bash
source build-func.sh
image_name="fs"
job_core_office_file="gradio-office-thumbs"

#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
rm -f $job_core_office_file
echo "
FROM linuxserver/libreoffice
RUN apk update
RUN apk upgrade
RUN apk add py3-pip
RUN apk add git
#COPY ./../docker-build/requirements/build-app-office.txt /app/office.req.txt
RUN python3 -m pip install gradio --break-system-packages
RUN python3 -m pip install webp  --break-system-packages
RUN python3 -m pip install pillow  --break-system-packages
#RUN python3 -m pip install -r /app/office.req.txt --no-cache-dir
COPY ./../app_services /app/app_services
RUN python3 /app/app_services/office_server_check.py
ENTRYPOINT [\"/usr/bin/env\"]
">>$job_core_office_file
job_core_office_tag=4
job_core_office_build="gradio.office.thumbs."$(tag $job_core_office_tag)
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
#docker run -it -p 8014:8014 nttlong/fs:gradio.office.thumbs.amd.1  python3 /app/app_services/office_server.py
