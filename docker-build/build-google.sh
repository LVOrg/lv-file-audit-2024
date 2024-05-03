#!/bin/bash
source build-func.sh
image_name="fs"
rm -f web-api-core
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
web_api_thumb_file="web-api-thumb-core"

rm -f $web_api_thumb_file
echo "
FROM python:3.10.13-bullseye
COPY ./../venv-google/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"python3\",\"/cmd/google_drive.py\"]
">>$web_api_thumb_file
web_api_thumb_core_tag=4
web_api_thumb_tag_build="fs.google."$(tag $web_api_thumb_core_tag)
web_api_thumb_image="$repository/fs:"web_api_thumb_tag_build
buildFunc $web_api_thumb_file $repository $image_name $web_api_thumb_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
