#!/bin/bash

content=$(kubectl get nodes -o go-template="{{range .items}}{{.metadata.name}} {{end}}")

# Extract worker names using grep and awk
workers=$(echo "$content" | grep -E '(^worker:|\<none\>)')
  # Filter lines starting with "worker:"
# shellcheck disable=SC2206
workers=(${workers// / })  # Split each line on space and store in an array
workers=("${workers[@]%*}")  # Remove everything after the first space from each element

# Print the list of worker nodes
echo "List of worker nodes:"
echo "${workers[@]}"
