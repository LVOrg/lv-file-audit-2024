import threading

import pika
import uuid
import subprocess
import time


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


def execute_command_with_polling(command):
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
            if line:
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
