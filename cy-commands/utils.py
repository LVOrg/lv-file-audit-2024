import signal
import threading
import typing

import pika
import uuid
import subprocess
import time
import psutil
import os


def send_message_and_wait(message, queue_name: str, host: str = "localhost"):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    correlation_id = str(uuid.uuid4())
    properties = pika.BasicProperties(correlation_id=correlation_id)
    channel.basic_publish(exchange="", routing_key=queue_name, body=message, properties=properties)
    response = None

    # Consume messages from the temporary queue (optional callback)
    def on_response(ch, method, props, body):
        nonlocal response
        response = body.decode()
        ch.stop_consuming()  # Stop consuming after receiving the response

    channel.queue_declare(queue=f"{queue_name}_result")

    channel.basic_consume(queue=f"{queue_name}_result", on_message_callback=on_response, auto_ack=True)
    channel.start_consuming()
    connection.close()
    return response


def execute_command_with_polling(command, command_handler=None):
    """
  Executes a command line and prints output while it's running.

  Args:
      command: A string representing the command to execute.
  """

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    ret_text = ""
    while process.poll() is None:
        # Check for new output periodically (adjust interval as needed)
        try:
            line = process.stdout.readline().decode()
            print(line)
            if line:
                if callable(command_handler):
                    command_handler(line)
                else:
                    print(line, end='')  # Print without newline to avoid extra line breaks
                    ret_text += line + "\n"
        except:
            continue
        time.sleep(0.1)  # Adjust sleep time for desired polling frequency

    # Wait for the command to finish and get the final output
    output, error = process.communicate()

    return ret_text


def create_listener(channel, queue_name: str, host: str = "localhost"):
    correlation_id = str(uuid.uuid4())

    def process_message(channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        output = execute_command_with_polling(body.decode())
        channel.basic_publish(exchange="", routing_key=f"{queue_name}_result", body=str(output).encode())

    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=process_message)
    channel.start_consuming()


def socat_watcher(port: int, processor: typing.Callable) -> typing.Tuple[subprocess.Popen, threading.Thread]:
    assert callable(processor), "processor must be a function"

    command = f"socat tcp4-listen:{port} -"
    process = subprocess.Popen(f"socat -u TCP-LISTEN:{port},fork,reuseaddr -",
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               shell=True,
                               stdin=subprocess.PIPE)

    def running(process, processor):
        while process.poll() is None:
            # Check for new output periodically (adjust interval as needed)
            try:
                line = process.stdout.readline().decode()
                if line:
                    print(line)
                    if callable(processor):
                        ret = processor(line)
                        if isinstance(ret, str):
                            process.stdin.write(ret.encode())
                            process.stdin.flush()  # Ensure the input is sent
                        else:
                            text_to_send = f"{line} is ok\n"
                            process.stdin.write(text_to_send.encode())
                            process.stdin.flush()  # Ensure the input is sent
            except:
                continue
            time.sleep(0.1)  # Adjust sleep time for desired polling frequency
        output, error = process.communicate()

    th = threading.Thread(target=running, args=(process, processor,))
    th.start()
    return process, th
    # Wait for the command to finish and get the final output


def get_pid_using_port(port):
    """
  This function retrieves the PID of the process using a specified port.

  Args:
      port (int): The port number to check for.

  Returns:
      int: The PID of the process using the port, or None if no process is using it.
  """

    try:
        # Get a list of established TCP connections
        connections = psutil.net_connections(kind='tcp')

        # Filter connections by port number
        for conn in connections:
            if conn.laddr.port == port:
                return conn.pid

        return None

    except (PermissionError, psutil.NoSuchProcess):
        # Handle potential permission errors or unavailable processes
        print(f"Error: Couldn't access process information for port {port}.")
        return None


def kill_process(pid):
    """
  This function attempts to kill a process with the specified PID.

  Args:
      pid (int): The process ID (PID) of the process to terminate.
  """

    try:
        # Send SIGTERM signal for a graceful termination (recommended)
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM signal to process {pid}.")
    except ProcessLookupError:
        print(f"Process with PID {pid} not found.")
    except PermissionError:
        print(f"Insufficient permissions to kill process {pid}.")
