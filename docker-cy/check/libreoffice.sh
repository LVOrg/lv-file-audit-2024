#!/bin/sh
soffice --headless --convert-to png --outdir /check /check/libreoffice.sh
killall soffice;exit 0
#soffice --headless --convert-to png --outdir /home/vmadmin/python/v6/file-service-02/docker-cy/check /home/vmadmin/python/v6/file-service-02/docker-cy/check/tes2.mpx
#projectlibre --headless --convert-to png --outdir /home/vmadmin/python/v6/file-service-02/docker-cy/check /home/vmadmin/python/v6/file-service-02/docker-cy/check/test.mpp