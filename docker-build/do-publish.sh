#!/bin/bash

# Set the source and destination image tags
source_image="docker.lacviet.vn/xdoc/fs-tiny-qc-1:latest"
destination_image="docker.lacviet.vn/xdoc/fs-tiny-massan:latest"

# Pull the source image
docker pull "$source_image"

# Tag the pulled image with the destination name
docker tag "$source_image" "$destination_image"

# Push the tagged image to the destination registry
docker push "$destination_image"