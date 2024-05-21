#!/bin/bash
source build-func.sh
image_name="fs"
rm -f web-api-core
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
web_api_thumb_file="web-api-thumb-core"

rm -f $web_api_thumb_file
echo "
FROM python:3.10.13-bullseye
COPY ./../env-img-process/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY ./../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"python3\",\"/cmd/thumb.py\"]
">>$web_api_thumb_file
web_api_thumb_core_tag=2
if [ -z "$3" ]; then
  # No argument provided, use default repository
  web_api_thumb_tag_build=$web_api_thumb_core_tag
else
  # Argument provided, use it as the repository
  web_api_thumb_tag_build=$3
fi

#web_api_thumb_image="$repository/fs:"web_api_thumb_tag_build
buildFunc $web_api_thumb_file $repository "lv-thumbs-$customer" $web_api_thumb_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
