#!/bin/bash
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
image_name="fs"
source build-func.sh
docker_file_path="jobs.tesseract"
rm -f $docker_file_path
echo "
FROM clearlinux/tesseract-ocr
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata
COPY ./../../../../../usr/share/tesseract-ocr/5/tessdata /usr/share/tesseract-ocr/5/tessdata
COPY ./../cy_tesseract_api /app
RUN python -m pip install -r /app/cy_tesseract_api/requirement.txt
ENTRYPOINT []
">>$docker_file_path
tesseract_api_tag=1
tesseract_api_tag_build="api.tesseract."$(tag $tesseract_api_tag)
tesseract_api_image=$repository/$image_name:$tesseract_api_tag_build
buildFunc $docker_file_path $repository $image_name $tesseract_api_tag_build "python:3.10-alpine" "alpine"
#buildFunc $ai_file $repository $image_name $ai_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"