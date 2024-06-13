#!/bin/bash
start_time=$(date +%s.%N)

#sudo apt update -y
sudo apt-get install sshpass -y

source ./client-libs.sh
# shellcheck disable=SC2207
echo "start"
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
  client_prompt "Which version? (correctly, type version in one of above list): "
  # shellcheck disable=SC2034
  read enter_version
  while [[ $(lib_value_is_in_list "$enter_version" "$versions_list_check") == "no" ]]; do
    # shellcheck disable=SC2059
    client_prompt "Which version? (correctly, type version in one of above list): "
    # shellcheck disable=SC2034
    read enter_version

  done
  else
    enter_version=$1
fi
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
      config_dict["$master_ip"]="$master_password"
      echo "Connection successful!"
      break
    else
         client_prompt "Enter password of $master_ip: "
          stty -echo
          read -r master_password
          stty echo
    fi
done
workers_ips=($(client_get_worker_ips))
for ip in "${workers_ips[@]}"; do
    not_ok=true
    client_prompt "Enter password of $ip: "
    stty -echo
    read -r master_password
    stty echo
    while [[ $not_ok ]]; do
      client_remote_exec "$master_password" "$ip" "echo \"Connected is successful!\""
        if [ $? -eq 0 ]; then
          echo "Connection successful!"
          config_dict["$ip"]="$master_password"
          break
        else
             client_prompt "Enter password of $ip: "
              stty -echo
              read -r master_password
              stty echo
        fi
    done
done

install_master(){
  client_prompt "Now installing for  $master_ip: "
  local password="${config_dict["$master_ip"]}"

  client_copy_resource "$password" "$master_ip"
  client_remote_exec "$password" "$master_ip" "chmod +x /tmp/k8s-install/master.sh"
  client_remote_exec "$password" "$master_ip" "/tmp/k8s-install/master.sh $enter_version"
}
install_worker(){
  ip=$1
  local password="${config_dict["$ip"]}"
  echo "$password"
  client_prompt "Now installing for  $ip: "
  client_copy_resource "$password" "$ip"
  client_remote_exec "$password" "$ip" "chmod +x /tmp/k8s-install/worker.sh"
  client_remote_exec "$password" "$ip" "/tmp/k8s-install/worker.sh $enter_version"
}
join_worker(){
  ip=$1
  j_cmd="$2"
  local password="${config_dict["$ip"]}"
  echo "$password"
  client_remote_exec "$password" "$ip" "kubeadm reset -f"
  client_remote_exec "$password" "$ip" "rm -fr \$HOME/.kube/config"
  client_prompt "join $ip ..."
  client_remote_exec "$password" "$ip" "$j_cmd"
}
install_master
for ip in "${workers_ips[@]}"; do
  install_worker $ip
done
client_prompt "Now! join all nodes"
master_password="${config_dict["$master_ip"]}"
j_cmd=$(client_remote_exec "$master_password" "$master_ip" "kubeadm token create --print-join-command")
client_prompt "$j_cmd"
for ip in "${workers_ips[@]}"; do
  join_worker "$ip" "$j_cmd"
done
end_time=$(date +%s.%N)

# Calculate the elapsed time with nanosecond precision
elapsed_time=$(echo "$end_time - $start_time" | bc)

# Extract integer seconds and nanoseconds (avoiding floating-point issues)
int_seconds=${elapsed_time%%.*}
nanoseconds=${elapsed_time#*.}

# Convert nanoseconds to seconds (divide by 1 billion for nano to seconds)
nanoseconds_in_seconds=$(echo "scale=9; $nanoseconds / 1000000000" | bc)

# Total elapsed time in seconds (integer + nanoseconds converted to seconds)
total_seconds=$(echo "$int_seconds + $nanoseconds_in_seconds" | bc)

# Convert total elapsed time to hours, minutes, and seconds
# (this uses integer division and modulo to avoid floating-point math)
hours=$((total_seconds / 3600))
remainder=$((total_seconds % 3600))
minutes=$((remainder / 60))
seconds=$((remainder % 60))

# Format the time string (leading zeros for single-digit values)
formatted_time=$(printf "%02d:%02d:%02.3f" "$hours" "$minutes" "$seconds")

echo "Processing finished. Time taken: $formatted_time"
