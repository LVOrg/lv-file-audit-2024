#!/bin/bash
source  k8s-libs.sh
all_packages=$(lib_get_all_existing_packages)
echo "$all_packages"
# shellcheck disable=SC2034
for package in "${all_packages[@]}"; do
  yum remove "$all_packages" -y
done