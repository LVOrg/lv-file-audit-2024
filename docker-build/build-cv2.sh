#!/bin/bash
source build-func.sh
source kill-port.sh
port_number="${1:-8765}"  # Use 8765 as default if no argument provided
# Call the kill_port_process function with the port number
list_and_kill_port_processes 8765
image_name="fs"
job_core_file="job-cv2-core"

#nttlong/file-svc
repository="docker.io/nttlong"
#user="nttlong/file-svc"
platform=linux/amd64

#du -sh $(pwd)/../env_jobs_slim/lib/python3.10/site-packages/* | sort -h
rm -f $job_core_file
echo "
FROM docker.io/python:3.10.12-slim-bookworm
RUN apt update
#RUN apt install socat -y
COPY  ./../env_jobs_slim/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
RUN   apt update && apt install python3-opencv -y

COPY ./../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"python3\",\"/cmd/video.py\"]
">>$job_core_file
job_core_tag=5
job_core_tag_build="fs.cv2.core."$(tag $job_core_tag)
job_core_image=$repository/$image_name:$job_core_tag_build
buildFunc $job_core_file $repository $image_name $job_core_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
echo "docker run  -p 1111:1111  -v /socat-share:/socat-share  $repository/fs:$job_core_tag_build"
echo "docker run -it -p 8765:8765 nttlong/fs:fs.cv2.core.amd.1"
job_slim_file="video"
echo "
FROM $job_core_image
ARG TARGETARCH
ARG OS
COPY ./../cy-commands /cmd
RUN apt clean && apt autoclean
ENTRYPOINT [\"python3\",\"/cmd/video.py\"]
">>$job_slim_file
video_tag=1
video_tag_build="fs.video."$(tag $video_tag)
video_image=$repository/$image_name:$video_tag_build
buildFunc $job_slim_file $repository $image_name $video_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
echo "docker run  -p 1111:1111  -v /socat-share:/socat-share  $repository/fs:$video_tag_build"
