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
#RUN apt update && apt upgrade -y
#RUN apt install socat -y
RUN python3 -m pip install PyMuPDF
RUN python3 -m pip install gradio
COPY /../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"python3\",\"/cmd/pdf.py\"]
">>$build_file
ocr_core_tag=2
if [ -z "$3" ]; then
  # No argument provided, use default repository
  ocr_core_tag_build=$ocr_core_tag
else
  # Argument provided, use it as the repository
  ocr_core_tag_build=$3
fi

#ocr_core_image="$repository/fs:"$ocr_core_tag_build
buildFunc $build_file $repository "lv-pdf-$customer" $ocr_core_tag_build "python:3.10-alpine" "alpine"
echo "docker run -p 1112:1112  -v /socat-share:/socat-share $repository/$image_name:$ocr_core_tag_build"