#!/bin/bash
platform=linux/amd64
source build-func.sh
repository=docker.lacviet.vn/xdoc
ubuntu_net_80_file="ubuntu_net_80_file"
rm -fr $ubuntu_net_80_file
echo "
FROM dokken/ubuntu-22.04:latest
RUN apt update
RUN apt install dotnet-sdk-8.0 -y
RUN apt update
RUN apt-get install -y aspnetcore-runtime-8.0
RUN apt-get install -y dotnet-runtime-8.0
COPY ./../dot-net/so-files /usr/lib
RUN apt install software-properties-common -y
RUN add-apt-repository universe
RUN dotnet --version
EXPOSE 5000
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python3.12 -y
RUN apt install python3.12-dev -y
#RUN apt-get install python3.12-distutils -y
RUN apt install -y python3-pip
RUN python3 -m pip install --upgrade pip
COPY ./../dot-net/LV.OCR.API_linux-x64 /app
WORKDIR /app
ENTRYPOINT [\"dotnet\", \"LV.OCR.API.dll\"]
">>$ubuntu_net_80_file
ubuntu_net_80_file_tag=2
ubuntu_net_80_file_image=$ubuntu_net_80_file:$ubuntu_net_80_file_tag
#buildFunc $web_api_core_file "docker.io/nttlong" $image_name $web_api_core_tag_build "python:3.10-alpine" "alpine"
buildFunc $ubuntu_net_80_file $repository $ubuntu_net_80_file $ubuntu_net_80_file_tag "python:3.10-alpine" "alpine"
echo docker run -it $repository/$ubuntu_net_80_file_image /bin/bash