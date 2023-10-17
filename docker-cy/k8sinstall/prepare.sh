#!/bin/bash
echo "Prepare for network"
mkdir -p /proc
mkdir -p /proc/sys
mkdir -p /proc/sys/net
mkdir -p /proc/sys/net/bridge
cat <<< "1" | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables
mkdir -p /proc/sys/net/ipv4
cat <<< "1" | sudo tee /proc/sys/net/ipv4/ip_forward
#Prepare for kubelet service run
echo "Prepare for kubelet service run. In order to kubelet run ok we must turn of swap"
# First diasbale swap
sudo swapoff -a
# And then to disable swap on startup in /etc/fstab
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
