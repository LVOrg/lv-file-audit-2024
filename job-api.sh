#!/bin/bash
source ./env_webapi/bin/activate
uvicorn cy_jobs.web:app \
        --env-file $(pwd)/web-env/.env \
        --host 0.0.0.0 --port 8087 \
        --workers 1
        --reload
#uvicorn cy_xdoc.server:app \
#        --env-file $(pwd)/web-env/.env \
#        --host 0.0.0.0 --port 8012 \
#        --ssl-keyfile=$(pwd)/web-env/fs.key \
#        --ssl-certfile=$(pwd)/web-env/fs.crt \
#        --reload