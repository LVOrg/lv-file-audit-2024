#!/bin/bash
# shellcheck disable=SC2034
all_packages=$(source get-list-of-package.sh)
# shellcheck disable=SC2154
echo "sudo yum remove $all_packages "
  # shellcheck disable=SC2086
sudo yum remove $all_packages -y


#exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
version="$1"
echo "installing kubelet kubeadm kubectl with version is v$version"
rm -f /etc/yum.repos.d/kubernetes.repo
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v$version/rpm/
enabled=1
gpgcheck=0
gpgkey=https://pkgs.k8s.io/core:/stable:/v$version/rpm/repodata/repomd.xml.key

EOF
sudo systemctl stop kubeadmy
sudo systemctl stop kubectl
sudo systemctl stop containerd
sudo yum remove kubeadm kubelet kubectl kube-proxy containerd -y
sudo yum clean metadata
sudo yum clean all
sudo yum update -y && sudo yum upgrade -y
sudo yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes -y
sudo systemctl enable --now kubelet

#"sudo yum remove kubeadm-1.27.14-150500.1.1.x86_64 kubectl-1.27.14-150500.1.1.x86_64 kubelet-1.27.14-150500.1.1.x86_64"
#"sudo yum remove kubeadm.1.27.14-150500.1.1.x86_64 kubectl.1.27.14-150500.1.1.x86_64 kubelet.1.27.14-150500.1.1.x86_64"