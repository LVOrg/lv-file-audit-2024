#!/bin/bash

# Navigate to the directory containing listener.py (optional)
# Uncomment this line if your script needs to be run from the same directory
# cd "$(dirname "$0")"

# Run listener.py with the provided argument

script_path=$(readlink -f "${BASH_SOURCE[0]}")
script_dir=$(dirname "$script_path")

echo "Script location: $script_dir"
# Check if python3.9 is available
if [ -d "/cmd" ]; then
  if command -v python3.9 >/dev/null 2>&1; then
      python3.9 /cmd/sender.py "$@"  # Execute the command with python3.9 and arguments
    else
      echo "Python 3.9 not found, using python..."
      python3 /cmd/sender.py "$@"     # Execute the command with python and arguments
    fi
else
    echo "Python 3.9 not found, using python..."
    python3 $script_dir/sender.py "$@"     # Execute the command with python and arguments
fi