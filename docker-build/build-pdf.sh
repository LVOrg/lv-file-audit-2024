#!/bin/bash
#docker run -it  -v $(pwd)/../cy-commands:/cmd -v $(cms)/../tmp-files:/tmp-files -p 3456:3456  -v /socat-share:/socat-share --entrypoint /bin/bash  hdgigante/python-opencv:4.9.0-debian

source build-func.sh
image_name="fs"
rm -f build_file
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
build_file="pdf-prcoessing"
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
rm -f $build_file
echo "
FROM python:3.10.13-bullseye
COPY ./../venv-remote-pdf/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./../remote_server_libs /remote_server_libs
COPY ./../cy_file_cryptor /remote_server_libs/cy_file_cryptor
RUN apt clean && apt autoclean
ENTRYPOINT [\"/remote_server_libs/pdf.sh\"]
">>$build_file
ocr_core_tag=4


#ocr_core_image="$repository/fs:"$ocr_core_tag_build
buildFunc $build_file $repository "lv-pdf" $ocr_core_tag "python:3.10-alpine" "alpine"
echo "docker run -p 1112:1112  -v /socat-share:/socat-share $repository/$image_name:$ocr_core_tag_build"