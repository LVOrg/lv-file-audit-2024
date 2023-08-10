#!/bin/sh
apt update && apt-get install wget -y
apt install mono-complete -y nocache
apt-get install -y libicu-dev nocache
mkdir -p /usr/share/dotnet
wget https://download.visualstudio.microsoft.com/download/pr/7c62b503-4ede-4ff2-bc38-50f250a86d89/3b5e9db04cbe0169e852cb050a0dffce/dotnet-sdk-6.0.300-linux-arm64.tar.gz
tar -zxf dotnet-sdk-6.0.300-linux-arm64.tar.gz -C /usr/share/dotnet
rm dotnet-sdk-6.0.300-linux-arm64.tar.gz
wgethttps://download.visualstudio.microsoft.com/download/pr/8ba7087e-4513-41e5-8359-a4bcd2a3661f/e6828f0d8cf1ecc63074c9ff57685e27/aspnetcore-runtime-6.0.5-linux-arm64.tar.gz
    tar -zxf aspnetcore-runtime-6.0.5-linux-arm64.tar.gz -C /usr/share/dotnet
    rm aspnetcore-runtime-6.0.5-linux-arm64.tar.gz
        #wget -SL -o dotnet.tar.gz https://dotnetcli.blob.core.windows.net/dotnet/Sdk/master/dotnet-sdk-latest-linux-arm64.tar.gz;\

        #tar -zxf dotnet-sdk-latest-linux-arm64.tar.gz -C /usr/share/dotnet;\
ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet
dotnet --list-runtimes
python3 -m  pip install --upgrade pip
python3 -m pip uninstall pythonnet -y
python3 -m pip install pythonnet==3.0.1 --no-cache-dir