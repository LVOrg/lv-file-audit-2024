#!/bin/sh
apt update && apt-get install wget -y
apt install mono-complete -y nocache
wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
apt-get update
apt-get install -y dotnet-runtime-7.0\
apt-get update
apt-get install -y dotnet-sdk-7.0 nocache
dotnet --list-runtimes
python3 -m  pip install --upgrade pip
python3 -m pip uninstall pythonnet -y
python3 -m pip install pythonnet==3.0. --no-cache-dir
