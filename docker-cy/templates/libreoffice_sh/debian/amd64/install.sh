#!/bin/sh
apt update
apt-cache search openjdk | grep 17
apt install openjdk-17-jdk -y nocache
apt install openjdk-17-jre -y nocache
apt install libreoffice -y nocache
