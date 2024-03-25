#!/bin/bash
source build-func.sh
image_name="fs"
rm -f build_file
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
build_file="ocr-core"

rm -f $build_file
echo "
FROM ubuntu:20.04
RUN apt update && apt upgrade -y
#RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update
RUN apt install python3.9 -y
RUN apt install libopencv-dev -y
RUN apt install python3-opencv -y; exit 0;
RUN  apt-get update --fix-missing

RUN apt install python3-opencv -y
RUN apt install libgomp1 -y
RUN apt install socat -y
RUN apt install netcat -y
RUN apt install curl -y
RUN apt install wget -y
RUN apt install nano -y
RUN apt install git -y
#RUN pip install --upgrade pip
#COPY ./../docker-build/requirements/ocr.req.txt /app/ocr.req.txt
#RUN python3 -m pip install -r  /app/ocr.req.txt --no-cache-dir
COPY ./../env_ai_cloud/lib/python3.9/site-packages /usr/local/lib/python3.9/dist-packages
RUN apt install python3-pip && apt install libgomp1 -y && apt install python3-opencv -y
RUN apt clean && apt autoclean
">>$build_file
ocr_core_tag=1
ocr_core_tag_build="fs.ocr.core."$(tag $ocr_core_tag)
ocr_core_image="$repository/fs:"$ocr_core_tag_build
buildFunc $build_file $repository $image_name $ocr_core_tag_build "python:3.10-alpine" "alpine"

fs_ocr_file="fs.ocr"
rm -f $fs_ocr_file

echo "ARG BASE
FROM $ocr_core_image
RUN apt install python3-pip -y && python3.9 -m pip install pika

COPY ./../cy_command /cmd
ENTRYPOINT [\"/cmd/listener.sh\"]
">>$fs_ocr_file
fs_ocr_tag=1
fs_ocr_tag_build="fs.ocr."$(tag $ocr_core_tag).$fs_ocr_tag
fs_ocr_image=web:"apps".$web_api_core_tag_build
buildFunc $fs_ocr_file $repository $image_name $fs_ocr_tag_build "python:3.10-alpine" "alpine"