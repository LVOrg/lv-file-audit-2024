#!/bin/bash
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
if [ -z "$3" ]; then
  # No argument provided, use default repository
  version="latest"
else
  # Argument provided, use it as the repository
  version="$3"
fi
./build-tiny.sh $repository $customer $version
./build-office.sh "docker.io/nttlong" "libs"  "1"
#./build-thumbs.sh "docker.io/nttlong" "libs" "1"
./build-video.sh "docker.io/nttlong" "libs" "1"
./build-pdf.sh  "docker.io/nttlong" "libs" "1"