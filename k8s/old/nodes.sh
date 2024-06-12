#!/bin/bash
get_master_ip() {
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
get_worker_ips() {
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
