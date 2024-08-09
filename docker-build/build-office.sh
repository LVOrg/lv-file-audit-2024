#!/bin/bash
source build-func.sh
image_name="fs"
rm -f build_file
#nttlong/file-svc
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
#user="nttlong/file-svc"
platform=linux/amd64
build_file="office-core"

rm -f $build_file
echo "
FROM ubuntu:20.04
RUN apt update && apt upgrade -y
#RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update
RUN apt install libreoffice -y;exit 0
RUN  apt-get update --fix-missing
RUN apt install libreoffice -y
#COPy ./../venv-remote-office-38/lib/python3.8/site-packages /usr/local/lib/python3.8/dist-packages
#RUN python3 -c \"import sys;print(sys.version);import fastapi\"
#RUN apt install curl -y
#RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
#RUN python3 -m pip install fastapi
#COPY ./../remote_server_libs /app
RUN apt clean && apt autoclean
#ENTRYPOINT [\"/app/office.sh\"]
">>$build_file
ocr_office_tag=1
ocr_office_tag_build=$ocr_office_tag
ocr_office_image="$repository/fs:"$ocr_office_tag_build
buildFunc $build_file $repository "libre-office" $ocr_office_tag_build "python:3.10-alpine" "alpine"
echo "docker run -it -p 1113:1113 -v $(pwd)/../tmp-files:/tmp-files -v $(pwd)/../cy-commands:/cmd -v $(pwd)/../socat-share:/socat-share $repository/fs:fs.office.core.amd.1"
#docker run -p 3456:3456 -v /socat-share:/socat-share nttlong/fs:fs.office.core.amd.1
#docker run -p 3456:3456 -v /tmp-files:/tmp-files -v /home/vmadmin/python/cy-py/cy-commands:/cmd -v /socat-share:/socat-share nttlong/fs:fs.office.core.amd.1
#python3.9 /cmd/office.py /cmd/office.py abc
fs_office_file="office-python310"
rm -f $fs_office_file

echo "ARG BASE
FROM nttlong/libre-office:$ocr_office_tag_build
RUN apt-get install python3.10 -y
#COPY ./../cy_file_cryptor /remote_server_libs/cy_file_cryptor
#COPY ./../remote_server_libs /remote_server_libs
#COPY ./../cy-commands /cmd
#RUN apt-get update --fix-missing
RUN apt install python3-pip -y
#RUN python3.9 -m pip install gradio
RUN apt clean && apt autoclean
#ENTRYPOINT [\"python3.9\", \"/cmd/office.py\"]
">>$fs_office_file
fs_office_tag=1
if [ -z "$3" ]; then
  # No argument provided, use default repository
  fs_office_tag_build=$ocr_office_tag.$fs_office_tag
else
  # Argument provided, use it as the repository
  fs_office_tag_build=$3
fi
#fs_office_tag_build="fs.office."$(tag $ocr_office_tag).$fs_office_tag
fs_office_tag_build=$ocr_office_tag.$fs_office_tag
fs_ocr_image="lv-office-$customer".$web_api_core_tag_build
buildFunc $fs_office_file $repository "libreoffice-python310" $fs_office_tag_build "python:3.10-alpine" "alpine"
echo "docker run -p 1113:1113  -v /socat-share:/socat-share $repository/$image_name:$fs_office_tag_build"
#/usr/local/lib/python3.10/dist-packages
fs_office_file_final="libreoffice-python-310"
rm -f fs_office_file_final
echo "ARG BASE
FROM nttlong/libreoffice-python310:$fs_office_tag_build
COPY ./../venv-remote-office/lib/python3.10/site-packages /usr/local/lib/python3.10/dist-packages
COPY ./../remote_server_libs /remote_server_libs
COPY ./../cy_file_cryptor /remote_server_libs/cy_file_cryptor
ENTRYPOINT [\"/remote_server_libs/office.sh\"]
">>$fs_office_file_final
lv_libreoffice_tag=4
buildFunc $fs_office_file_final $repository "lv-libreoffice" $fs_office_tag_build$lv_libreoffice_tag "python:3.10-alpine" "alpine"
