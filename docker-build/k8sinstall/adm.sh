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
#scp root@172.16.7.94:/usr/bin/kubelet 172.16.7.91:/usr/bin/
#scp root@172.16.7.94:/usr/bin/kubeadm 172.16.7.91:/usr/local/bin
scp root@172.16.7.94:/usr/bin/containerd 172.16.7.91:/usr/local/bin
# /usr/lib/systemd/system/containerd.service
scp root@172.16.7.94:/usr/lib/systemd/system/containerd.service 172.16.7.91:/usr/lib/systemd/system
scp root@172.16.7.94:/usr/bin/kubectl 172.16.7.91:/usr/local/bin
scp root@172.16.7.94:/usr/bin/kubeadm 172.16.7.91:/usr/local/bin
scp -r root@172.16.7.94:/usr/lib/systemd/system/kubelet.service.d 172.16.7.91:/usr/lib/systemd/system/kubelet.service.d
#=/etc/kubernetes
scp -r root@172.16.7.94:/etc/kubernetes 172.16.7.91:/etc
scp -r root@172.16.7.94:/var/lib/kubelet 172.16.7.91:/var/lib
scp  root@172.16.7.94:/etc/sysconfig/kubelet 172.16.7.91:/etc/sysconfig
sco
scp  root@172.16.7.94:/etc/containerd/config.toml 172.16.7.91:/etc/containerd
scp  root@172.16.7.94:/etc/sysconfig/kubelet 172.16.7.91:/etc/sysconfig
scp  root@172.16.7.94:/usr/lib64/libelf.so.1 172.16.7.91:/usr/lib64
#/usr/sbin/conntrack
scp  root@172.16.7.94:/usr/sbin/conntrack 172.16.7.91:/usr/sbin
scp  root@172.16.7.94:/proc/sys/net/ipv4/vs/conntrack 172.16.7.91:/proc/sys/net/ipv4/vs
scp  root@172.16.7.94:/usr/sbin/ip 172.16.7.91:/usr/sbin
#/usr/sbin/ip
#/proc/sys/net/ipv4/vs/conntrack
#/usr/lib64/libelf.so.1
#dnf install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
#/etc/sysconfig/kubelet
 #/var/lib/kubelet
 #/usr/bin/kubelet
#/usr/bin/kubelet
#/usr/local/bin
scp -r root@172.16.7.94:/usr/bin/kubelet 172.16.7.91:/usr/bin
scp -r root@172.16.7.94:/usr/bin/kubelet 172.16.7.91:/usr/local/bin
scp -r root@172.16.7.94:/usr/bin/kubelet 172.16.7.91:/etc/containerd
#/etc/yum.repos.d
#/etc/containerd
scp -r root@172.16.7.94:/etc/yum.repos.d 172.16.7.91:/etc/yum.repos.d
scp -r root@172.16.7.94:/etc/containerd 172.16.7.91:/etc/containerd
scp  root@172.16.7.94:/usr/bin/containerd 172.16.7.91:/usr/bin
#/etc/containerd/config.toml
#/etc/sysconfig/kubelet
#/var/lib/kubelet
# /usr/lib/systemd/system/kubelet.service.d
#/usr/bin/kubeadm
#/etc/containerd/config.toml
scp root@172.16.7.94:/etc/containerd/config.toml 172.16.7.91:/etc/containerd
#/usr/bin/containerd
# And then to disable swap on startup in /etc/fstab
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab