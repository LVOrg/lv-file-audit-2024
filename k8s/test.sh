#!/bin/bash
source  k8s-libs.sh
source ./client-libs.sh
#sudo yum remove $1
#path_to_file=$(which $1)
#sudo rm -f $path_to_file
#
#sudo yum remove $1
master_password="l/\cviet2023"
master_ip="172.16.7.99"
j_cmd=$(client_remote_exec "$master_password" "$master_ip" "kubeadm token create --print-join-command")
echo "$j_cmd"
password="l/\cviet2023"
ip="172.16.7.97"
client_remote_exec "$password" "$ip" "$j_cmd"