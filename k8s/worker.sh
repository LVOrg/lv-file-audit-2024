#!/bin/bash
script_dir=$(dirname "$0")

echo "$script_dir/k8s-libs.sh"
source  $script_dir/k8s-libs.sh
#this file will install in master node

# shellcheck disable=SC2034
# declare some variable for screen format
red_background="\033[41m"
# shellcheck disable=SC2034
white_text="\033[37m"
# shellcheck disable=SC2034
reset_color="\033[0m"
#----end of declare-----
echo "Follow by below list of stable version"
# shellcheck disable=SC2207
versions_list=($(lib_get_online_versions))
# shellcheck disable=SC2068
for version in "${versions_list[@]}"; do
  echo "-$version"
done
# shellcheck disable=SC2116
# shellcheck disable=SC2034
versions_list_check=$(echo "${versions_list[@]}")
# shellcheck disable=SC2076
if [ $# -eq 0 ]; then
  printf "${red_background}${white_text}Which version? (correctly, type version in one of above list) :${reset_color}"
  # shellcheck disable=SC2034
  read enter_version
  while [[ $(lib_value_is_in_list "$enter_version" "$versions_list_check") == "no" ]]; do
    # shellcheck disable=SC2059
    printf "${red_background}${white_text}Which version? (correctly, type version in one of above list) :${reset_color}"
    # shellcheck disable=SC2034
    read enter_version

  done
  else
    enter_version=$1
fi
echo "Will install $enter_version"
reset_worker_node
lib_tear_down_node
lib_prepare
lib_install_containerd
#reset_repo "$enter_version"
#echo "lib_add_repo $enter_version"
reset_repo "$enter_version"
lib_add_repo_new_version "$enter_version"
cat /etc/yum.repos.d/kubernetes.repo
yum install kubelet kubeadm kubectl -y
#lib_install_component "kubelet" "$enter_version"
#lib_install_component "kubeadm" "$enter_version"
#create_kube_service
#fix_kubelet_service
#systemctl enable contaierd
#systemctl enable kubelet

systemctl deamon-reload
systemctl enable contaierd
systemctl enable kubelet
systemctl restart contaierd
systemctl restart kubelet
systemctl status kubelet
#nano /etc/systemd/system/kubelet.service.d/0-kubeadm.conf
#lib_reset_node
