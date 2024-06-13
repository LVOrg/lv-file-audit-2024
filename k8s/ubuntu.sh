#!/bin/bash
source ./client-libs.sh
# shellcheck disable=SC2207
echo "start"
master_ip=$(client_get_master_ip)
client_prompt "Enter password of $master_ip: "
stty -echo
read -r master_password
stty echo
client_remote_exec "$master_password" "$master_ip" "echo \"Connected is successful!\""
