#!/bin/bash
red_background="\033[41m"
white_text="\033[37m"
reset_color="\033[0m"
echo "Follow by below list of stable version"
source list-all-available-version.sh

extracted_versions=$(source list-all-available-version.sh)
# shellcheck disable=SC2034
fixed_versions=$(echo "$extracted_versions" | tr '\n' ' ')
while true; do
  printf "${red_background}${white_text}Which version? (correctly, type version in one of above list) :${reset_color}"
  read version

  # Check if version is present in the list using in operator
  if grep -q "$version" <<< "$fixed_versions"; then
    found=true
    break
  else
    printf "${red_background}${white_text}Error: Invalid version. Please choose from the list above.${reset_color}\n"
  fi
done
master_file="./command/master.txt"
worker_file="./command/worker.txt"
rm -fr $master_file
rm -fr $worker_file
echo "
cd /tmp/k8s
./install-components.sh $version
">>$master_file
echo "
cd /tmp/k8s
./install-components.sh $version false
">>$worker_file
. ./nodes.sh  # Source the script from the current directory
# Call the functions from nodes.sh
master_node=$(get_master_ip)

worker_nodes=($(get_worker_ips))


scp -r "$(pwd)" root@$master_node:"/tmp/k8s"
master_content=$(cat "./command/master.txt")
ssh -p 22 $master_node " bash -c \"$master_content\" "

for ip in "${worker_nodes[@]}"; do
      scp -r "$(pwd)" root@$ip:"/tmp/k8s"
      worker_content=$(cat "./command/worker.txt")
      ssh -p 22 $ip " bash -c \"$worker_content\" "
done
