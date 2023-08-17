#!/bin/sh

apt update
apt upgrade --force-yes
#apt install snap
#snap install libreoffice

#apt-cache search openjdk | grep 17
apt-get install openjdk-17-jdk -y nocache
apt-get install openjdk-17-jre -y nocache
apt-get install libreoffice -y nocache