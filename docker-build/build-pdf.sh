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

rm -f $build_file
echo "
FROM python:3.10.13-bullseye
RUN apt update && apt upgrade -y
RUN apt install socat -y
RUN pip install PyMuPDF
COPY /../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"/cmd/server-pdf.sh\"]
">>$build_file
ocr_core_tag=1
ocr_core_tag_build="fs.pdf."$(tag $ocr_core_tag)
ocr_core_image="$repository/fs:"$ocr_core_tag_build
buildFunc $build_file $repository $image_name $ocr_core_tag_build "python:3.10-alpine" "alpine"