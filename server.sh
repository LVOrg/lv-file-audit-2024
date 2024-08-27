#!/bin/bash
#source ./env_webapi/bin/activate
source ./web-api-312/bin/activate
uvicorn cy_xdoc.server:app \
        --env-file $(pwd)/web-env/.env \
        --host 0.0.0.0 --port 8012 \
        --workers 2
        --reload
#uvicorn cy_xdoc.server:app \
#        --env-file $(pwd)/web-env/.env \
#        --host 0.0.0.0 --port 8012 \
#        --ssl-keyfile=$(pwd)/web-env/fs.key \
#        --ssl-certfile=$(pwd)/web-env/fs.crt \
#        --reload