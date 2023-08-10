#!/bin/sh
export TAG='rc.0.0.4'
docker buildx   build -t nttlong/xdoc-torch-dataset-huggingface:$TAG  --platform=linux/amd64,linux/arm64/v8  ./.. -f torch-dataset-huggingface  --push=true --output type=registry
docker buildx   build -t nttlong/xdoc-torch-dataset-layout-microsoft:$TAG  --platform=linux/amd64,linux/arm64/v8  ./.. -f torch-dataset-layout-microsoft  --push=true --output type=registry
docker buildx   build -t nttlong/xdoc-torch-dataset-layouts:$TAG  --platform=linux/amd64,linux/arm64/v8  ./.. -f torch-dataset-layouts  --push=true --output type=registry