#!/bin/bash
source  k8s-libs.sh
lib_install_component "kubelet" $1
if [ $? -ne 0 ]; then
  lib_install_component "kubelet" $1
fi