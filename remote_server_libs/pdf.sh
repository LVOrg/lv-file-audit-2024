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
echo "python3 /remote_server_libs/pdf_api.py port=$PORT"
python3 $(pwd)/remote_server_libs/pdf_api.py port=$PORT

# Handle potential errors from the Python script (optional)
if [[ $? -ne 0 ]]; then
  echo "Error: office.py exited with code $?."
  exit 1
fi

# Keep the container running (optional)
# Comment out this line if your office.py script exits after execution
# trap "" SIGTERM SIGINT  # trap signals to prevent immediate exit
# sleep infinity          # Keeps the container running indefinitely