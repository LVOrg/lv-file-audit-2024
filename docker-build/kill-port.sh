# Function to kill processes using port 8765
list_and_kill_port_processes() {
  port_number="$1"

  # Find process IDs and PIDs associated with the port using lsof
  processes=$(sudo lsof -i :"$port_number" -p | awk '{print $2,$9}')

  if [[ -n "$processes" ]]; then
    echo "Processes using port $port_number:"
    echo "$processes"  # Display PID and command name for each process
    echo

    # Prompt user for confirmation before killing
    read -r -p "Kill these processes (y/N)? " response
    if [[ "$response" =~ ^([Yy]|[Yy]es)$ ]]; then
      for pid in $(awk '{print $1}' <<< "$processes"); do
        echo "Killing process $pid..."
        sudo kill -TERM "$pid"  # Send SIGTERM for graceful termination
        sleep 2  # Wait for process to terminate
      done
    else
      echo "Processes not killed."
    fi
  else
    echo "No processes found using port $port_number."
  fi
}
