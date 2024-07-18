#!/bin/bash

# Check if the port argument is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a port number as an argument."
  exit 1
fi

# Assign the port to a variable
PORT=$1

# Run your Python script with the provided port
# Assuming office.py is the main script
echo "python3 /remote_server_libs/office.py port=$PORT"
python3.10 /remote_server_libs/ocr.py port=$PORT

# Handle potential errors from the Python script (optional)
if [[ $? -ne 0 ]]; then
  echo "Error: office.py exited with code $?."
  exit 1
fi