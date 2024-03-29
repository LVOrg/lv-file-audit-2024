#!/bin/bash
socat -u  TCP4-LISTEN:3456,fork,reuseaddr EXEC:/bin/bash
#at client socat STDIN TCP4:localhost:3456