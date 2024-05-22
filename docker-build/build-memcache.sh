#!/bin/bash
source build-func.sh
#image_name="fs"
rm -f build_file
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
build_file="mc-build"

rm -f $build_file
echo "
FROM debian:unstable-slim
RUN apt update
RUN apt install memcached -y
RUN apt install libmemcached-tools -y
RUN apt clean && apt autoclean
">>$build_file
ocr_core_tag=2
ocr_core_tag_build=1
buildFunc $build_file $repository "mc" $ocr_core_tag_build "python:3.10-alpine" "alpine"


