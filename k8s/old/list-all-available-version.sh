#!/bin/bash

# Define the URL
url="https://kubernetes.io/releases/"

# Fetch the content using curl and capture the output in a variable
content=$(curl -s "$url")

# Use grep and cut on the content variable
versions=$(grep -Eo '[v][0-9]+.[0-9]+.[0-9]+' <<< "$content" | cut -d '>' -f2)


# Filter lines with '.' and remove duplicates using sort and uniq
filtered_versions=$(grep -Eo '.*\..*' <<< "$versions" | sort -u)
# Print each version on a new line (optional)
echo "$filtered_versions"