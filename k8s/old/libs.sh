#!/bin/bash

# Function to extract and return URLs
# how to call function in this file
# incude this file into runing file by using
# source
get_kubeadm_urls() {
  # Download and process HTML content (same as before)
  query=$1
  local html_content=$(curl -s https://www.rpmfind.net/linux/rpm2html/search.php?query=$query&submit=Search+...&system=&arch=aarch64)
  html_content=$(echo "$html_content" | iconv -f ISO-8859-1 -t UTF-8)
  html_content=$(echo "$html_content" | grep -Eo '<table>.*?</table>')

  # Extract elements and URLs (same as before)
  elements=($(echo "$html_content" | grep -Eo '<a [^>]*href=[^']*.aarch64.rpm[^']*[^>]*>' | tr -d '\n'))
  local hrefs=()
  for element in "${elements[@]}"; do
    href=${element#'}
    href=${href%'}
    hrefs+=("$href")
  done
  local urls=()
  for x in "${hrefs[@]}"; do
    url=$(sed -n "s/^.*'\(.*\)'.*$/\1/p" <<< $x)
    urls+=("$url")
  done

  # Print or return URLs (modify as needed)
  # Option 1: Print URLs
  echo "Extracted URLs:"
  for url in "${urls[@]}"; do
    echo "$url"
  done

  # Option 2: Return URLs (for use in another script)
  echo "${urls[@]}"
}
urls=($(get_kubeadm_urls "kubelet"))
for x in "${urls[@]}"; do
 echo "$x"
done
