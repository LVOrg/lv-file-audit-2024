#!/bin/bash
trap 'SIG_IGN' CHLD
socat -u  TCP4-LISTEN:3456,fork,reuseaddr EXEC:/bin/bash
#at client socat STDIN TCP4:localhost:3456
#/usr/bin/soffice --headless --convert-to png /cmd/server.sh /cmd
#    /usr/bin/soffice --headless --convert-to png /cmd/server.sh /socat-share
# /usr/bin/soffice --headless --convert-to png --outdir "/socat-share" /cmd/server.sh