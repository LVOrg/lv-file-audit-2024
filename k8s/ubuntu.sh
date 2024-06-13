#!/bin/bash
#sudo apt update -y
sudo apt-get install sshpass -y

source ./client-libs.sh
# shellcheck disable=SC2207
echo "start"
# shellcheck disable=SC2034
declare -A config_dict

master_ip=$(client_get_master_ip)

# shellcheck disable=SC2034
not_ok=true
client_prompt "Enter password of $master_ip: "
stty -echo
read -r master_password
stty echo
while [[ $not_ok ]]; do
  client_remote_exec "$master_password" "$master_ip" "echo \"Connected is successful!\""
    if [ $? -eq 0 ]; then
      echo "Connection successful!"
      break
    else
         client_prompt "Enter password of $master_ip: "
          stty -echo
          read -r master_password
          stty echo
    fi
done
config_dict["$master_password"]="$master_password"
echo "$config_dict"
install_master(){

  client_copy_resource "$master_password" "$master_ip"
  client_remote_exec "$master_password" "$master_ip" "chmod +x /tmp/k8s-install/master.sh"
  client_remote_exec "$master_password" "$master_ip" "/tmp/k8s-install/master.sh 1.26"
}
install_master & wait
# shellcheck disable=SC2207
# shellcheck disable=SC2034
workers_ips=($(client_get_worker_ips))
for ip in "${workers_ips[@]}"; do
    client_prompt "Enter password of $ip: "
    stty -echo
    read -r master_password
    stty echo
done