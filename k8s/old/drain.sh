#!/bin/bash
# Check Kubernetes version using kubectl version
# shellcheck disable=SC1068
red_background="\033[41m"
white_text="\033[37m"
reset_color="\033[0m"
# Prompt the user with colored text using printf

sudo kubectl get node
printf "${red_background}${white_text}Type node name in above list:${reset_color}"

# Read the user's input
read node_name

# shellcheck disable=SC2207
worker_list=$(kubectl get nodes -o go-template="{{range .items}}{{.metadata.name}} {{end}}")


# shellcheck disable=SC2199
# shellcheck disable=SC2076
while [[ ! "${worker_list[@]}" =~ "$node_name" ]]; do
  # shellcheck disable=SC2128
  printf "${red_background}${white_text}Type node name in above list:${reset_color}"
  read node_name
done
echo "Draining node: $node_name"
k8s_version=$(sudo kubectl version| grep "Server Version:" | cut -d ' ' -f 3)
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

echo "sudo kubectl drain $node_name --ignore-daemonsets $drain_flag"
sudo kubectl drain $node_name --ignore-daemonsets $drain_flag --force
sudo kubectl cordon $node_name --force
sudo kubectl delete node $node_name --grace-period=0 --force

