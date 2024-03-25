#!/bin/bash

# Start listening on port 8080
nc -l 8080 &
pid=$!  # Capture the background process PID

# Wait for the background process (nc) to finish
wait $pid

# Extract received data from nc (limited to the first line by default)
data=$(head -n 1 < /dev/tcp/localhost/8080)

# Write the received data to a file
echo "$data" >> /home/vmadmin/python/cy-py/docker-build/received_data.txt

echo "Server stopped."