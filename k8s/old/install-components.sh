#!/bin/bash

source k8s-libs


# Prompt the user with a question
# shellcheck disable=SC2034
red_background="\033[41m"
white_text="\033[37m"
reset_color="\033[0m"
source tear-down.sh
sh step2.sh "$1"

if [ $? -ne 0 ]; then

  sh step2.sh "$1"
  if [ $? -ne 0 ]; then
    sh step2.sh "$1"
    if [ $? -ne 0 ]; then
      sh step2.sh "$1"
    fi
  fi
fi
source container-d.sh
reset_node(){
  kubeadm reset -f
  rm -fr $HOME/.kube/config
  rm -fr /etc/kubernetes/manifests/etcd.yaml
  rm -fr  /etc/kubernetes/manifests/kube-scheduler.yaml
  rm -fr /etc/kubernetes/manifests/kube-apiserver.yaml
  rm -fr /etc/kubernetes/manifests/kube-controller-manager.yaml
}
init_kubeadm() {
kubeadm reset -f
rm -fr $HOME/.kube/config
rm -fr /etc/kubernetes/manifests/etcd.yaml
rm -fr  /etc/kubernetes/manifests/kube-scheduler.yaml
rm -fr /etc/kubernetes/manifests/kube-apiserver.yaml
rm -fr /etc/kubernetes/manifests/kube-controller-manager.yaml
systemctl start kubelet
output=$(kubeadm init --v=5 2>&1)

# Check the exit code of the command
exit_code=$?

# Analyze the output and exit code
if [ $exit_code -ne 0 ]; then
    kubeadm reset -f
    rm -fr $HOME/.kube/config
    rm -fr /etc/kubernetes/manifests/etcd.yaml
    rm -fr  /etc/kubernetes/manifests/kube-scheduler.yaml
    rm -fr /etc/kubernetes/manifests/kube-apiserver.yaml
    rm -fr /etc/kubernetes/manifests/kube-controller-manager.yaml
    if [ $exit_code -ne 0 ]; then
      output=$(kubeadm init --v=5 2>&1)
      if [ $exit_code -ne 0 ]; then
         echo "$output"
      else
        echo "kubeadm init successful!"
      fi
    else
      echo "kubeadm init successful!"
    fi
else
  echo "kubeadm init successful!"
fi
clear
kubeadm token create --print-join-command
}
second_arg=${2:-true}
if [[ "$second_arg" == "true" ]]; then
  init_kubeadm
else
  # Command to execute when the second argument is something other than "true"
  reset_node
  echo "Install worker is ok"
fi


