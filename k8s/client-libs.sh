#!/bin/bash
red_background="\033[41m"
# shellcheck disable=SC2034
white_text="\033[37m"
# shellcheck disable=SC2034
reset_color="\033[0m"
function lib_get_online_versions() {
  #this function will return list of online version at official web page
  url="https://kubernetes.io/releases/"
  content=$(curl -s "$url")
  versions=$(grep -Eo '[v][0-9]+.[0-9]+.[0-9]+' <<< "$content" | cut -d '>' -f2)
  filtered_versions=$(grep -Eo '.*\..*' <<< "$versions" | sort -u)
  fixed_versions=$(echo "$filtered_versions" | tr '\n' ' ')
  echo "$fixed_versions"

}
function client_prompt() {
    # shellcheck disable=SC2059
    printf "${red_background}${white_text}$1${reset_color}"
}
function client_get_master_ip() {
  # Read the first line containing "master" from nodes.txt
  master_line=$(grep -m 1 "^master:" nodes.txt)

  # Check if a line was found
  if [[ -n "$master_line" ]]; then
    # Extract the IP address (assuming format: master:user@IP)
    master_ip=$(echo "$master_line" | cut -d ':' -f 2 | tr -d '[:space:]')  # Remove leading/trailing spaces
    # Return the extracted IP (modified line)
    # shellcheck disable=SC2151
    echo "$master_ip"
  fi
}
function client_get_worker_ips() {
  # Read the line containing "workers" from nodes.txt
  worker_line=$(grep -m 1 "^workers:" nodes.txt)
  ips=()
  # Check if a worker line was found
  if [[ -n "$worker_line" ]]; then
    # Extract comma-separated worker entries (remove leading "workers:")
    worker_entries=${worker_line#*:}
    # shellcheck disable=SC2206
    text_list=(${worker_entries//,/ })
    for element in "${text_list[@]}"; do
      ips+=("$element")
    done
    # Print worker entries directly (modified line)
    echo "${ips[@]}"
  else
    echo "Error: Line containing 'workers' not found in nodes.txt"
  fi
}


function client_remote_exec() {
  #sshpass -p "l/\cviet2023" scp -r "$(pwd)" root@172.16.7.99:"/tmp/k8s-install"
  # shellcheck disable=SC2034
  password=$(echo "$1")

  # shellcheck disable=SC2034
  rm_host="root@$2"
  # shellcheck disable=SC2034
  rm_cmd="$3"
  sshpass -p "$password" ssh "$rm_host" "$rm_cmd"

}
function client_copy_resource() {
    client_remote_exec $1 $2 "rm -fr /tmp/k8s-install"
    # shellcheck disable=SC2140
    sshpass -p "$1" scp -r "$(pwd)" root@"$2":"/tmp/k8s-install"
}
function client_get_join_command() {
    master_ip="$2"
    # shellcheck disable=SC2034
    master_password="$1"

}