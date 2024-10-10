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
RUN apt install tesseract-ocr -y
RUN apt-get update && apt-get install -y \
    libleptonica-dev \
    libtesseract-dev

RUN ln -s /usr/lib/x86_64-linux-gnu/libdl.so.2 /usr/lib/x86_64-linux-gnu/libdl.so
#&& \
#    mkdir -p /LV.OCR.API/x64 && \
#    ln -s /usr/lib/x86_64-linux-gnu/liblept.so.5 /LV.OCR.API/x64/libleptonica-1.82.0.so && \
#    ln -s /usr/lib/x86_64-linux-gnu/libtesseract.so.5 /LV.OCR.API/x64/libtesseract50.so
#check /usr/lib/x86_64-linux-gnu/libtesseract50.so
#check /usr/lib/x86_64-linux-gnu/libleptonica-1.82.0.so
WORKDIR /app
ENTRYPOINT [\"dotnet\", \"LV.OCR.API.dll\"]
RUN apt clean && apt autoclean
">>$ubuntu_net_80_file
ubuntu_net_80_file_tag=5
ubuntu_net_80_file_image=$ubuntu_net_80_file:$ubuntu_net_80_file_tag
#buildFunc $web_api_core_file "docker.io/nttlong" $image_name $web_api_core_tag_build "python:3.10-alpine" "alpine"
buildFunc $ubuntu_net_80_file $repository $ubuntu_net_80_file $ubuntu_net_80_file_tag "python:3.10-alpine" "alpine"
echo docker run -it $repository/$ubuntu_net_80_file_image /bin/bash
#docker run -it --entrypoint=/bin/bash -v  /root/python-2024/lv-file-fix-2024/py-files-sv/dot-net/LV.OCR.API_linux-x64:/app docker.lacviet.vn/xdoc/ubuntu_net_80_file:4
#docker run  -it -v  /root/python-2024/lv-file-fix-2024/py-files-sv/dot-net/LV.OCR.API_linux-x64:/app -v /root/python-2024/lv-file-fix-2024/py-files-sv/dot-net/so-files:/so-files ubuntu:22.04 /bin/bash
#docker run  -p 5000:5000 docker.lacviet.vn/xdoc/ubuntu_net_80_file:5

#apt-get update && apt-get install -y    wget    gnupg     ca-certificates  libssl-dev    libffi-dev    libgdiplus    libxrender1  libx11-6  && rm -rf /var/lib/apt/lists/*