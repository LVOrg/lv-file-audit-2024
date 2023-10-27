#!/bin/bash
source build-func.sh
image_name="fs"
rpc_file="rpc"
rm -f $rpc_file
#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64


rm -f $rpc_file
echo "
FROM python:3.10-alpine
RUN apk add git
RUN pip install --upgrade pip
RUN python3 -m pip install git+https://github.com/Sudo-VP/Vietnamese-Word-Segmentation-Python.git
COPY ./../docker-build/requirements/web-api.req.txt /app/web-api.req.txt
RUN python3 -m pip install -r  /app/web-api.req.txt --no-cache-dir
COPY ./../cy_grpc /app/cy_grpc
COPY ./../RPC_serverless_check.py /app/RPC_serverless_check.py
">>$rpc_file
rpc_tag=7
rpc_tag_build="test.rpc."$(tag $rpc_tag)
rpc_image="$repository/fs:"$rpc_tag_build
buildFunc $rpc_file $repository $image_name $rpc_tag_build "python:3.10-alpine" "alpine"
echo "in order to check image run:"
echo "docker run -it -v \$(pwd)/..:/app --entrypoint bash nttlong/fs:$rpc_tag_build  /bin/bash"
echo "python3 /app/RPC_serverless_check.py"
echo "python3 /app/cy_consumers/files_extrac_text_from_image.py"
