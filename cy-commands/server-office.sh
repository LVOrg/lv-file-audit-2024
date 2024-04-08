#!/bin/bash
echo "start 1113"
socat -u  TCP4-LISTEN:1113,fork,reuseaddr EXEC:/bin/bash
#at client socat STDIN TCP4:localhost:8765
#/usr/bin/soffice --headless --convert-to png /cmd/server.sh /cmd
#    /usr/bin/soffice --headless --convert-to png /cmd/server.sh /socat-share
# /usr/bin/soffice --headless --convert-to png --outdir "/socat-share" /cmd/server.sh