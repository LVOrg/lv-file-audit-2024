#!/bin/bash

# Navigate to the directory containing listener.py (optional)
# Uncomment this line if your script needs to be run from the same directory
# cd "$(dirname "$0")"

# Run listener.py with the provided argument


# Check if python3.9 is available
if [ -d "/cmd" ]; then
  if command -v python3.9 >/dev/null 2>&1; then
      python3.9 /cmd/listener.py "$@"  # Execute the command with python3.9 and arguments
    else
      echo "Python 3.9 not found, using python..."
      python3 /cmd/listener.py "$@"     # Execute the command with python and arguments
    fi
else
    if command -v python3.9 >/dev/null 2>&1; then
      python3.9 listener.py "$@"  # Execute the command with python3.9 and arguments
    else
      echo "Python 3.9 not found, using python..."
      python3 listener.py "$@"     # Execute the command with python and arguments
    fi
fi
