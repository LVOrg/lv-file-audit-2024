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
build_file="ocr-mypdf-api"

rm -f $build_file
echo "
FROM jbarlow83/ocrmypdf
RUN apt update && apt upgrade -y
RUN apt-get install tesseract-ocr-vie -y
COPY ./../docker-build/requirements/ocrmypdf.txt /app/ocrmypdf.txt
RUN pip install -r /app/ocrmypdf.txt
COPY ./../remote_server_libs /remote_server_libs
COPY ./../cy_file_cryptor /remote_server_libs/cy_file_cryptor
ENTRYPOINT [\"/remote_server_libs/ocr.sh\"]
">>$build_file
ocr_office_tag=12
ocr_office_tag_build=$ocr_office_tag
ocr_office_image="$repository/ocr-my-pdf:"$ocr_office_tag_build
buildFunc $build_file $repository "ocr-my-pdf-api" $ocr_office_tag_build "python:3.10-alpine" "alpine"

