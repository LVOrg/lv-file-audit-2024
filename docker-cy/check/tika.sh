#!/bin/sh
python3 -m pip uninstall tika -y
python3 -m pip install tika==1.25
python3 /check/tika_server.py
killall java; exit 0