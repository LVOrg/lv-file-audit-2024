#!/bin/bash


# Process each line in the text


all_versions=$(sudo yum list kubelet kubeadm kubectl --show-duplicates | grep @)


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