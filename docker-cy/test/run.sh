#!/bin/sh
echo "docker exec -it $(hostname) bash"
python3 -c 'import time;time.sleep(100000000)'