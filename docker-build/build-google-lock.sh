#!/bin/bash
source build-func.sh
image_name="fs"
rm -f web-api-core
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
web_api_thumb_file="google-lock"

rm -f $web_api_thumb_file
echo "
FROM python:3.10.13-bullseye
COPY ./../venv-google/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./../remote_server_libs /remote_server_libs
RUN apt clean && apt autoclean
ENTRYPOINT [\"/remote_server_libs/google-lock.sh\"]
">>$web_api_thumb_file
web_api_thumb_core_tag=1
web_api_thumb_tag_build="google-lock"$(tag $web_api_thumb_core_tag)
#web_api_thumb_image="$repository/fs:"web_api_thumb_tag_build
buildFunc $web_api_thumb_file  $repository "google-lock" $web_api_thumb_core_tag "docker.io/python:3.10.12-slim-bookworm" "debian"