#!/bin/bash
# Prompt the user with a question
# shellcheck disable=SC2034
red_background="\033[41m"
white_text="\033[37m"
reset_color="\033[0m"
# Prompt the user with colored text using printf
printf "${red_background}${white_text}Do you want to tear down your node? (y/N):${reset_color}"

# Read the user's input
read answer

# Convert the answer to lowercase for case-insensitive comparison (optional)
answer=$(tr [A-Z] [a-z] <<< "$answer")


# Check if the user entered 'y' or pressed Enter (assumed as yes)
if [[ "$answer" == "y" ]]; then
  # Tear down the node logic goes here (replace with your commands)
  echo "OK! we will clear all below:"
  all_versions=$(sudo yum list kubelet kubeadm kubectl --show-duplicates | grep @)
  echo $all_versions

  source tear-down.sh
else
  echo "Node teardown cancelled."
fi
echo "Follow by below list of stable version"
source list-all-available-version.sh

extracted_versions=$(source list-all-available-version.sh)
# shellcheck disable=SC2034
fixed_versions=$(echo "$extracted_versions" | tr '\n' ' ')
while true; do
  printf "${red_background}${white_text}Which version? (correctly, type version in one of above list) :${reset_color}"
  read version

  # Check if version is present in the list using in operator
  if grep -q "$version" <<< "$fixed_versions"; then
    found=true
    break
  else
    printf "${red_background}${white_text}Error: Invalid version. Please choose from the list above.${reset_color}\n"
  fi
done

install_kubelet_kubeadm="step2.sh"
sh step2.sh "$version"
if [ $? -ne 0 ]; then

  sh step2.sh "$version"
  if [ $? -ne 0 ]; then
    sh step2.sh "$version"
    if [ $? -ne 0 ]; then
      sh step2.sh "$version"
    fi
  fi
fi
source container-d.sh