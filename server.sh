#!/bin/bash
uvicorn cy_xdoc.server:app \
        --env-file $(pwd)/web-env/.env \
        --host 0.0.0.0 --port 8012 \
        --ssl-keyfile=$(pwd)/web-env/fs.key \
        --ssl-certfile=$(pwd)/web-env/fs.crt \
        --reload