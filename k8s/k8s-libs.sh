#!/bin/bash
# Convention:
# in this libs: all function begin with "lib_get_" will return value
# all function begin with lib_get_ and end with 's' will return a list
# In another sh file call return list function must be quote by "()"
# Example:
#   version = ($(lib_get_online_versions))
# This file declare all necessary function for k8s install
# how to call function in this file
# include this file into running file by using
# source  k8s-libs.sh
# call function
# example:
#   lib_reset_node
#------------usage--------------
# lib_reset_node: reset k8s node
# lib_prepare: using before install k8s
# lib_get_online_versions: get list of online version
#   Example:
# quot by "()" for return list function
#     version = ($(lib_get_online_versions))
# lib_get_all_existing_packages: get all installed packages
# lib_install_all_componentsL install kubeadm, kubelet, kube-proxy
# Example
#     lib_install_all_components 1.30
#     if [ $? -ne 0 ]; then
#       echo "loi roi"
#     else
#     echo "Thanh cong
#     fi
function lib_reset_node(){
  #this function will reset node by using kubeadm reste
  kubeadm reset -f
  rm -fr $HOME/.kube/config
  rm -fr /etc/kubernetes/manifests/etcd.yaml
  rm -fr  /etc/kubernetes/manifests/kube-scheduler.yaml
  rm -fr /etc/kubernetes/manifests/kube-apiserver.yaml
  rm -fr /etc/kubernetes/manifests/kube-controller-manager.yaml
}
function lib_prepare() {
  #this function will prepare installing
    lib_reset_node
    echo "Prepare for network"
    mkdir -p /proc
    mkdir -p /proc/sys
    mkdir -p /proc/sys/net
    mkdir -p /proc/sys/net/bridge
    cat <<< "1" |  tee /proc/sys/net/bridge/bridge-nf-call-iptables
    mkdir -p /proc/sys/net/ipv4
    cat <<< "1" |  tee /proc/sys/net/ipv4/ip_forward
    #Prepare for kubelet service run
    echo "Prepare for kubelet service run. In order to kubelet run ok we must turn of swap"
    # First diasbale swap
     swapoff -a
    # And then to disable swap on startup in /etc/fstab
     sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
}
function lib_get_online_versions() {
  #this function will return list of online version at official web page
  url="https://kubernetes.io/releases/"
  content=$(curl -s "$url")
  versions=$(grep -Eo '[v][0-9]+.[0-9]+.[0-9]+' <<< "$content" | cut -d '>' -f2)
  filtered_versions=$(grep -Eo '.*\..*' <<< "$versions" | sort -u)
  fixed_versions=$(echo "$filtered_versions" | tr '\n' ' ')
  echo "$fixed_versions"

}
function lib_get_all_existing_packages() {
   #This function will get all exiting resource of k8s was install in node

    all_versions=$( yum list kubelet kubeadm kubectl --show-duplicates | grep @)
        items=""
        # Process each line in the text
        while IFS= read -r line; do
          # shellcheck disable=SC2206
          cols=(${line// / })

        # Extract name (everything before the first dot) and architecture (everything after)
          name="${cols[0]%.*}"  # Remove everything after the first dot
          arc="${cols[0]#*.}"  # Remove everything before the first dot


          # Extract version and type (assuming format)
          version=${cols[1]}
          package_name=" $name-$version.$arc"
          # shellcheck disable=SC2206
          items+="$package_name"
        done <<< "$all_versions"
        # shellcheck disable=SC2128
        echo "$items"
}
function lib_install_containerd() {
  yum-config-manager --disable kubernetes
 yum-config-manager --save --setopt=kubernetes.skip_if_unavailable=true

   yum clean metadata
       yum clean all
   yum update -y &&  yum upgrade -y
  # shellcheck disable=SC2046
   yum install $(yum list | grep missing)
    cat <<EOF | tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
modprobe overlay && \
modprobe br_netfilter
yum install yum-utils -y
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install containerd.io -y
CONTAINDERD_CONFIG_PATH=/etc/containerd/config.toml && \
rm "${CONTAINDERD_CONFIG_PATH}" && \
containerd config default > "${CONTAINDERD_CONFIG_PATH}" && \
sed -i "s/SystemdCgroup = false/SystemdCgroup = true/g"  "${CONTAINDERD_CONFIG_PATH}"
systemctl enable --now containerd && \
systemctl restart containerd
}
function lib_drain_node() {
  local node_name=$1
  k8s_version=$( kubectl version| grep "Server Version:" | cut -d ' ' -f 3)
  if [[ -z "$k8s_version" ]]; then
    echo "Error: Could not determine Kubernetes version. Ensure 'kubectl' is installed and accessible."
    exit 1
  fi
  # shellcheck disable=SC2034
  major_version=${k8s_version%%.*}
  minor_version=${k8s_version#*.}

  # Convert minor version to number
  minor_version=${minor_version%%.*}  # Remove trailing patch version (if any)

  # Compare minor version with 120
  if [[ $minor_version -ge 20 ]]; then
    # Kubernetes version 1.20 or later (use --delete-emptydir-data)
    drain_flag="--delete-emptydir-data"
    echo "Kubernetes version: $k8s_version (use --delete-emptydir-data)"
  else
    # Kubernetes version before 1.20 (use --delete-local-data, but deprecated)
    drain_flag="--delete-local-data"
    echo "Warning: --delete-local-data is deprecated. Consider upgrading to Kubernetes 1.20 or later."
    echo "Kubernetes version: $k8s_version (use --delete-local-data with caution)"
  fi
  echo " kubectl drain $node_name --ignore-daemonsets $drain_flag"
   kubectl drain "$node_name" --ignore-daemonsets "$drain_flag" --force
   kubectl cordon "$node_name" --force
   kubectl delete node "$node_name" --grace-period=0 --force
}
function lib_get_all_nodes() {
    content=$(kubectl get nodes -o go-template="{{range .items}}{{.metadata.name}} {{end}}")
    workers=$(echo "$content" | grep -E '(^worker:|\<none\>)')
      # Filter lines starting with "worker:"
    # shellcheck disable=SC2206
    workers=(${workers// / })  # Split each line on space and store in an array
    workers=("${workers[@]%*}")  # Remove everything after the first space from each element

    # Print the list of worker nodes
    echo "List of worker nodes:"
    echo "${workers[@]}"
}
function lib_add_repo_old_version() {
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
}
function lib_add_repo_new_version() {
  if [ -z "$1" ]; then
  echo "Error: Missing argument!"
  exit 1  # Raise an error with exit code 1
fi
    rm -f /etc/yum.repos.d/kubernetes.repo
  cat <<EOF |  tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v$1/rpm/
enabled=1
gpgcheck=0
gpgkey=https://pkgs.k8s.io/core:/stable:/v$1/rpm/repodata/repomd.xml.key
EOF
cat /etc/yum.repos.d/kubernetes.repo
}
# shellcheck disable=SC2120
function lib_add_repo() {
  if [ -z "$1" ]; then
  echo "Error: Missing argument! at $(pwd)/k8s-libs.sh/lib_add_repo"
  exit 1  # Raise an error with exit code 1
fi
    rm -f /etc/yum.repos.d/kubernetes.repo
  cat <<EOF |  tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v$1/rpm/
enabled=1
gpgcheck=0
gpgkey=https://pkgs.k8s.io/core:/stable:/v$1/rpm/repodata/repomd.xml.key
EOF

#  if [[ "$(echo "$version" '> 1.27')" == "true" ]]; then
#    echo "-------------new version------------"
#    lib_add_repo_new_version "$version"
#  else
#    echo "-------------old version------------"
#    lib_add_repo_old_version "$version"
#  fi
}
function reset_repo() {

    lib_add_repo $1
    if [ $? -ne 0 ]; then
       # shellcheck disable=SC2028
       echo "Error at $(pwd)/k9s-libs.sh/reset_repo\n$?"
       exit 1
    fi
     yum clean all
     yum update
     yum upgrade
    # shellcheck disable=SC2046
     yum install $(yum list | grep missing) -y

     yum-complete-transaction --cleanup-only
     yum history redo last -y
     yum clean packages
}
function lib_install_component() {
      yum update -y
        yum clean all -y
    echo "installing  $1 with version is v$2"
     yum remove $1 -y
    path_to_file=$(which $1)
    rm -fr "$path_to_file"
     yum install $1  -y
if [ $? -ne 0 ]; then

        yum update -y
        yum clean all -y
        yum install $1  -y

    if [ $? -ne 0 ]; then

        yum update -y
        yum clean all -y
        yum install $1  -y

    if [ $? -ne 0 ]; then

       echo "Can not install $1"
       exit 1
       fi
       fi
    fi
#  if [ $? -ne 0 ]; then
#    echo "re installing kubelet kubeadm $1 with version is v$2"
#
#    subscription-manager repos --disable=kubernetes
#     yum install $1 --disablerepo=kubernetes -y
#     yum-config-manager --save --setopt=kubernetes.skip_if_unavailable=true
#
#     if [ $? -ne 0 ]; then
#       echo "Can not install $1"
#       exit 1
#    fi
#    exit $?
#  fi
  echo "install $1 ok"
}
function lib_install_all_components_master() {



    # shellcheck disable=SC2207
    all_packages=($(lib_get_all_existing_packages))
    for pkg in "${all_packages[@]}"; do
      echo "will remove $pkg"
       yum remove $pkg -y
    done


    # shellcheck disable=SC2086

    version="$1"
#     systemctl stop kubeadm || true
#     systemctl stop kubectl|| true
#     systemctl stop containerd|| true
##   yum remove kubeadm -y
#     yum remove kubelet -y
#     yum remove kubectl -y
##   yum remove kube-proxy -y
#     yum remove containerd -y
#     yum clean metadata|| true
#     yum clean all|| true
#     yum update -y &&  yum upgrade -y
  # shellcheck disable=SC2046

  reset_repo
  lib_add_repo
  lib_install_component "kubelet" "$version"
  lib_install_component "kubeadm" "$version"
  lib_install_component "kubectl" "1.30"
  # yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes -y
    systemctl enable --now kubelet
}
function lib_install_all_components_worker() {



    all_packages=($(lib_get_all_existing_packages))
    for pkg in "${all_packages[@]}"; do
      echo "will remove $pkg"
       yum remove $pkg -y
    done
  # shellcheck disable=SC2046
   yum install $(yum list | grep missing)
  reset_repo
  lib_add_repo
  lib_install_component "kubelet" $version
  lib_install_component "kubeadm" $version
  # yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes -y

}
function lib_tear_down_node() {
  #There are unfinished transactions remaining. You might consider running yum-complete-transaction, or "yum-complete-transaction --cleanup-only" and "yum history redo last", first to finish them. If those don't work you'll have to try removing/installing packages by hand (maybe package-cleanup can help).

      service_file="/lib/systemd/system/kubelet.service"
      service_file_usr="/lib/systemd/system/kubelet.service"
      service_ect_file="/etc/systemd/system/kubelet.service"
      rm -fr "$service_file"
      rm -fr "$service_file_usr"
      rm -fr "$service_ect_file"
      ctr -n k8s.io i rm $(ctr -n k8s.io i ls -q | grep your_filter)
      rm -rm /etc/sysconfig/kubelet

       yum-complete-transaction --cleanup-only
#       yum history redo last -y
       yum remove kubeadm -y
       yum remove kubelet  -y
       yum remove kubectl  -y
       yum remove kubernetes-cni  -y
       yum remove kube-apiserver  -y
       yum remove kube-controller-manager  -y
       yum remove  -y
       yum remove kube-scheduler  -y
       yum remove kube-proxy -y
       rm -rf /etc/kubernetes /var/lib/kubelet /var/lib/etcd -y
       yum remove docker docker-engine -y
       systemctl stop docker
       systemctl disable docker
       rm -rf /var/lib/docker -y

      all_packages=$(lib_get_all_existing_packages)
      for package in "${all_packages[@]}"; do
        yum remove $all_packages -y
      done
      # shellcheck disable=SC2154
      echo " yum remove $all_packages "
        # shellcheck disable=SC2086

       yum update -y
       yum clean metadata
       yum clean all
       yum update -y
       yum install deltarpm -y
       yum update -y
       yum-complete-transaction --cleanup-only
#       yum history redo last
       rm -fr /usr/lib/systemd/system/kubelet.service.d
       yum reinstall centos-release -y


}
function lib_value_is_in_list() {
  # Check if two arguments are passed (value and list)
  if [ $# -ne 2 ]; then
    echo "Usage: lib_value_is_in_list <value> <list>"
    return 1  # Indicate an error
  fi

  # Assign the arguments to variables
  local value="$1"
  # shellcheck disable=SC2116
  # shellcheck disable=SC2155
  local list=$(echo "$2")
  if grep -w "$value" <<< "$list"; then
    echo "yes"
  else
    echo "no"
  fi

}
function reset_master_node() {
   rm -fr /etc/yum.repos.d
   mkdir -p /etc/yum.repos.d
     systemctl stop kube-apiserver kube-controller-manager kube-scheduler kubelet
    systemctl disable kubelet
    rm -rf /etc/kubernetes/* /var/lib/kubernetes/*
    rm -rf /etc/kubernetes/* /var/lib/kubelet/* /var/lib/kube-apiserver/* /var/lib/kube-controller-manager/* /var/lib/kube-scheduler/*
    yum remove kubeadm -y
    systemctl stop etcd
     rm -rf /var/lib/etcd/*
#     systemctl start etcd


}
function reset_worker_node() {
   rm -fr /etc/yum.repos.d
   mkdir -p /etc/yum.repos.d
     systemctl stop kube-apiserver kube-controller-manager kube-scheduler
    systemctl disable kubelet
    rm -rf /etc/kubernetes/* /var/lib/kubernetes/*
    rm -rf /etc/kubernetes/* /var/lib/kubelet/* /var/lib/kube-apiserver/* /var/lib/kube-controller-manager/* /var/lib/kube-scheduler/*
    yum remove kubeadm -y
    systemctl stop etcd
     rm -rf /var/lib/etcd/*
#     systemctl start etcd


}
function lib_master_node_get_join_command() {
    kubeadm token create --print-join-command

}
function lib_master_export_config_for_kubectl_command() {
    export KUBECONFIG=/etc/kubernetes/admin.conf
    export KUBECONFIG=$HOME/.kube/config
    mkdir -p $HOME/.kube
     cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
     chown $(id -u):$(id -g) $HOME/.kube/config
     chown $(id -u):$(id -g) /etc/kubernetes/admin.conf
}
function lib_master_init() {
    # shellcheck disable=SC2005

    echo "$(kubeadm init --v=5)"
}
function create_kube_service_master(){
kubelet_path="$(which kubelet)"
    content="
[Unit]
Description=kubelet: The Kubernetes Node Agent
Documentation=https://kubernetes.io/docs/
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=/usr/bin/kubelet
Restart=always
StartLimitInterval=0
RestartSec=10

[Install]
WantedBy=multi-user.target

"
service_file="/lib/systemd/system/kubelet.service"
service_file_usr="/lib/systemd/system/kubelet.service"
service_ect_file="/etc/systemd/system/kubelet.service"
rm -fr "$service_file"
rm -fr "$service_file_usr"
rm -fr "$service_ect_file"
echo "$content" > "$service_file"
echo "$content" > "$service_file_usr"
echo "$content" > "$service_ect_file"
}
function create_kube_service() {
  kubelet_path="$(which kubelet)"
    content="[Unit]
Description=kubelet: The Kubernetes Node Agent
Documentation=https://kubernetes.io/docs/
Wants=network-online.target
After=network-online.target

[Service]
Environment=\"KUBELET_KUBECONFIG_ARGS=--bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf\"
Environment=\"KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml\"
ExecStart=$kubelet_path \$KUBELET_KUBECONFIG_ARGS \$KUBELET_CONFIG_ARGS
Restart=always
StartLimitInterval=0
RestartSec=10

[Install]
WantedBy=multi-user.target
"
service_file="/lib/systemd/system/kubelet.service"
service_file_usr="/lib/systemd/system/kubelet.service"
rm -fr "$service_file"
rm -fr "$service_file_usr"
echo "$content" > "$service_file"
echo "$content" > "$service_file_usr"
}
function fix_kubelet_service() {
  # shellcheck disable=SC2034
  rm -fr /usr/lib/systemd/system/kubelet.service.d
  mker -p /usr/lib/systemd/system/kubelet.service.d
  kubelet_path="$(which kubelet)"
    # shellcheck disable=SC2034
    REPLACEMENT_CONTENT="[Service]
Environment=\"KUBELET_KUBECONFIG_ARGS=--bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf\"
Environment=\"KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml\"
# Commenting out these lines as they are not strictly necessary for kubelet to function
#EnvironmentFile=-/var/lib/kubelet/kubeadm-flags.env
#EnvironmentFile=-/etc/sysconfig/kubelet
#ExecStart=/usr/bin/kubelet \$KUBELET_KUBECONFIG_ARGS \$KUBELET_CONFIG_ARGS
#ExecStart=$kubelet_path \$KUBELET_KUBECONFIG_ARGS \$KUBELET_CONFIG_ARGS
ExecStart=$kubelet_path \$KUBELET_KUBECONFIG_ARGS \$KUBELET_CONFIG_ARGS
"
#/usr/lib/systemd/system/kubelet.service.d
TARGET_FILE="/usr/lib/systemd/system/kubelet.service.d/0-kubeadm.conf"
# shellcheck disable=SC2034
rm -fr "/etc/systemd/system/kubelet.service.d"
rm -fr "/usr/lib/systemd/system/kubelet.service.d"
mkdir -p "/etc/systemd/system/kubelet.service.d"
mkdir -p "/usr/lib/systemd/system/kubelet.service.d"
TARGET_FILE_NON_USER="/etc/systemd/system/kubelet.service.d/0-kubeadm.conf"
TARGET_FILE10="/usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf"
# shellcheck disable=SC2034
#TARGET_FILE_NON_USER10="/etc/systemd/system/kubelet.service.d/10-kubeadm.conf"
#/etc/systemd/system/kubelet.service.d
#/etc/systemd/system/kubelet.service.d/0-kubeadm.conf
# Check if the target file exists
#if [ ! -f "$TARGET_FILE" ]; then
#  echo "Error: Target file '$TARGET_FILE' does not exist."
#  exit 1
#fi

# Backup the target file (optional)
#cp -p "$TARGET_FILE" "$TARGET_FILE.bak"  # Comment out this line if you don't want a backup

# Replace the content in the target file
#echo "$REPLACEMENT_CONTENT" > "$TARGET_FILE"
#echo "$REPLACEMENT_CONTENT" > "$TARGET_FILE_NON_USER"
#echo "$REPLACEMENT_CONTENT" > "$TARGET_FILE10"
#echo "$REPLACEMENT_CONTENT" > "$TARGET_FILE_NON_USER10"
echo "Successfully replaced content in '$TARGET_FILE'"
}
#/etc/systemd/system/kubelet.service.d/0-kubeadm.conf
#/usr/lib/systemd/system/kubelet.service.d
function lib_load_package() {
    package_list=()
    while read -r line; do
      IFS=': '  # Set internal field separator
      read -r name url <<<"$line"  # Read and split the line

      # Check if splitting resulted in name and url variables
      if [[ ! -z "$name" && ! -z "$url" ]]; then
          data=("$name","$url")
          package_list+=("${data[@]}")
      else
        echo "Error: Line '$line' has invalid format"  # Handle invalid lines (optional)
      fi

      unset IFS
  # Perform actions on the line variable here
done < ./repo/$1.txt
echo "${package_list[@]}"
}
function helm_install() {
  #curl -L "$url" -o /tmp/my-download/test.rpm

    mkdir -p /tmp/tmp-k8s-download
    curl -L https://get.helm.sh/helm-v3.x.x-linux-x86_64.tar.gz -o /tmp/tmp-k8s-download/helm.tar.gz
    tar -zxvf /tmp/tmp-k8s-download/helm.tar.gz
    sudo mv linux-x86_64/helm /usr/local/bin/helm

}
function install_calico() {
#    curl -L https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml -o /tmp/tmp-k8s-download/calico.yaml
    kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml
}