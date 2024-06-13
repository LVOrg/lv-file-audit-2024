#!/bin/bash
source  k8s-libs.sh
#sudo yum remove $1
#path_to_file=$(which $1)
#sudo rm -f $path_to_file
#
#sudo yum remove $1
lst=($(lib_load_package "1.30"))

for x in "${lst[@]}"; do
  echo "$x"
done
