#!/bin/bash
echo "start  at ... 1111"
socat -u  TCP4-LISTEN:1111,fork,reuseaddr EXEC:/bin/bash
#at client socat STDIN TCP4:localhost:1111
#/usr/bin/soffice --headless --convert-to png /cmd/server.sh /cmd
#    /usr/bin/soffice --headless --convert-to png /cmd/server.sh /socat-share
# /usr/bin/soffice --headless --convert-to png --outdir "/socat-share" /cmd/server.sh