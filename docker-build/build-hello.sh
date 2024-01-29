#!/bin/bash
source build-func.sh
image_name="fs"
rm -f web-api-core
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64
web_api_core_file="test-hello-world"

rm -f $web_api_core_file
echo "
FROM python:3.10.13-bullseye
COPY ./../docker-build/requirements/hello-world.txt /app/hello-world.txt
RUN python3 -m pip install -r  /app/hello-world.txt --no-cache-dir
COPY ./../cy_hello_world /app/cy_hello_world
">>$web_api_core_file
web_api_core_tag=2
web_api_core_tag_build="test.hello.world."$(tag $web_api_core_tag)
web_api_core_image="$repository/fs:"$web_api_core_tag_build
buildFunc $web_api_core_file $repository $image_name $web_api_core_tag_build "python:3.10-alpine" "alpine"

