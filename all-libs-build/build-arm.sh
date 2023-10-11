#!/bin/sh
chmod +x ./bkit.sh
docker run -it --platform=linux/arm64/v8 -v $(pwd)/..:/build  nttlong/py310-cython:1 /bin/bash
