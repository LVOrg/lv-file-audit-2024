#!/bin/bash
sudo yum remove kubeadm -y
sudo yum remove kubelet  -y
sudo yum remove kubectl  -y
sudo yum remove kubernetes-cni  -y
sudo yum remove kube-apiserver  -y
sudo yum remove kube-controller-manager  -y
sudo yum remove  -y
sudo yum remove kube-scheduler  -y
sudo yum remove kube-proxy -y
sudo rm -rf /etc/kubernetes /var/lib/kubelet /var/lib/etcd -y
sudo yum remove docker docker-engine -y
sudo systemctl stop docker
sudo systemctl disable docker
sudo rm -rf /var/lib/docker -y

all_packages=$(source get-list-of-package.sh)
# shellcheck disable=SC2154
echo "sudo yum remove $all_packages "
  # shellcheck disable=SC2086
sudo yum remove $all_packages -y
sudo yum update -y
sudo yum clean metadata
sudo yum clean all
sudo yum update -y
sudo yum install deltarpm -y
sudo yum update -y