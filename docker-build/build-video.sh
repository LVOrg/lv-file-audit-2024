#!/bin/bash
source build-func.sh
source kill-port.sh
port_number="${1:-8765}"  # Use 8765 as default if no argument provided
# Call the kill_port_process function with the port number
list_and_kill_port_processes 8765
image_name="fs"
job_core_file="job-cv2-core"

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
if [ -z "$3" ]; then
  # No argument provided, use default repository
  video_tag_build=$video_tag
else
  # Argument provided, use it as the repository
  video_tag_build=$3
fi

video_image=$repository/$image_name:$video_tag_build
buildFunc $job_slim_file $repository "lv-video-$customer" $video_tag_build "docker.io/python:3.10.12-slim-bookworm" "debian"
echo "docker run  -p 1111:1111  -v /socat-share:/socat-share  $repository/fs:$video_tag_build"
