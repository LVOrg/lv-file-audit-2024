#!/bin/bash
sudo yum remove kubeadm kubelet kubectl kube-proxy containerd -y
sudo yum clean metadata
sudo yum clean all
sudo yum update -y && sudo yum upgrade -y
sudo yum install deltarpm -y
all_packages=$(source get-list-of-package.sh)
# shellcheck disable=SC2154
echo "sudo yum remove $all_packages "
  # shellcheck disable=SC2086
sudo yum remove $all_packages -y
sudo yum update -y && sudo yum upgrade -y
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
sudo yum update -y