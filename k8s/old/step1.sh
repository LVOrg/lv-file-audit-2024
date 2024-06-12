#!/bin/bash
if [ -z "$1" ]; then
  echo "Error: Please provide a version as the first argument."
  exit 1
fi
version="$1"
# Call the extract_versions.sh script and capture its output
extracted_versions=$(source list-all-available-version.sh)
# shellcheck disable=SC2034
fixed_versions=$(echo "$extracted_versions" | tr '\n' ' ')

# Now you can use the extracted_versions variable
# shellcheck disable=SC2076
# shellcheck disable=SC1072
# shellcheck disable=SC1073

if grep -q "$version" <<< "$fixed_versions"; then
  echo "Value '$version' is found in the $fixed_versions."
else
  echo "Error: Version '$1' is not found in the list of stable versions."
  echo "$extracted_versions"
  echo "Stable versions are:"
    for version in $extracted_versions; do
      echo "  - $version"
    done
  exit 1
fi
