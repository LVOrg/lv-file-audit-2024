#!/bin/bash
yum update
yum upgrade
systemctl stop docker
yum remove docker-ce -y
rm -rf /var/lib/docker
yum update
yum install -y yum-utils

yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce
yum install -y docker-ce-cli
yum install -y containerd.io
yum install -y docker-compose-plugin
systemctl start docker
yum update
docker run busybox ls
#CentOS 7 needs to forward IP when running a Kubernetes cluster
# because the Kubernetes API server needs to be accessible from outside the cluster.
# The Kubernetes API server is the central component of the Kubernetes cluster,
# and it is responsible for managing all of the resources in the cluster.
systemctl stop firewalld
systemctl disable firewalld
cat << EOF > /proc/sys/net/ipv4/ip_forward
1
EOF
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
yum update
#------------------------
swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://yum.kubernetes.io/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
       https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
yum install -y kubeadm kubectl kubelet
sudo systemctl enable --now kubelet
# First diasbale swap
sudo swapoff -a

# And then to disable swap on startup in /etc/fstab
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab