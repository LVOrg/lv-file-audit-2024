#!/bin/bash

docker run --name video-1111 -p 1111:1111  -v /socat-share:/socat-share  docker.io/nttlong/fs:fs.video.amd.1 -d &
docker run --name pdf-1112 -p 1112:1112  -v /socat-share:/socat-share  docker.io/nttlong/fs:fs.pdf.amd.2 -d &
docker run --name office pdf-1113  -p 1113:1113  -v /socat-share:/socat-share  docker.io/nttlong/fs.office.amd.1.4 -d &
docker run --name tika-9998 -p 9998:9998  apache/tika