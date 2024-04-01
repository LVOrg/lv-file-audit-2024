#!/bin/bash
source build-func.sh
image_name="fs"
rm -f build_file
#nttlong/file-svc
repository="docker.io/nttlong"
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
RUN apt install python3.9 -y
RUN apt install libreoffice -y
RUN  apt-get update --fix-missing
RUN apt install libreoffice -y
RUN apt install socat -y
COPY ./../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"/cmd/server.sh\"]
">>$build_file
ocr_office_tag=1
ocr_office_tag_build="fs.office.core."$(tag $ocr_office_tag)
ocr_office_image="$repository/fs:"$ocr_office_tag_build
buildFunc $build_file $repository $image_name $ocr_office_tag_build "python:3.10-alpine" "alpine"
#docker run -p 3456:3456 -v /socat-share:/socat-share nttlong/fs:fs.office.core.amd.1
#docker run -p 3456:3456 -v /tmp-files:/tmp-files -v /home/vmadmin/python/cy-py/cy-commands:/cmd -v /socat-share:/socat-share nttlong/fs:fs.office.core.amd.1
#python3.9 /cmd/office.py /cmd/office.py abc
fs_office_file="fs.office"
rm -f $fs_office_file

echo "ARG BASE
FROM $ocr_office_image
COPY ./../cy-commands /cmd
ENTRYPOINT [\"/cmd/server.sh\"]
">>$fs_office_file
fs_office_tag=1
fs_office_tag_build="fs.office."$(tag $ocr_office_tag).$fs_office_tag
fs_ocr_image=web:"apps".$web_api_core_tag_build
buildFunc $fs_office_file $repository $image_name $fs_office_tag_build "python:3.10-alpine" "alpine"
