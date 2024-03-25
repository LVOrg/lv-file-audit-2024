import pika
import argparse
import subprocess

import time

def execute_command_with_polling(command):
  """
  Executes a command line and prints output while it's running.

  Args:
      command: A string representing the command to execute.
  """

  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

  while process.poll() is None:
    # Check for new output periodically (adjust interval as needed)
    line = process.stdout.readline().decode()
    if line:
      print(line, end='')  # Print without newline to avoid extra line breaks
    time.sleep(0.1)  # Adjust sleep time for desired polling frequency

  # Wait for the command to finish and get the final output
  output, error = process.communicate()
  if error:
    print(f"\nError: {error.decode()}")

  print(f"\nCommand finished with exit code: {process.returncode}")

def on_message_received(channel, method, properties, body):
  """
  Callback function to process received messages.

  Args:
      channel: The RabbitMQ channel.
      method: Message delivery method information.
      properties: Message properties.
      body: The message body (bytes).
  """
  message = body.decode()
  print(message)

  execute_command_with_polling(message)
  channel.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message processing



if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Consume messages from a RabbitMQ queue.')
  parser.add_argument('queue_name', help='The name of the queue to consume from.')
  parser.add_argument('host', help='The name of the queue to consume from.',default="localhost")
  args = parser.parse_args()

  # Define connection parameters (adjust if needed)
  connection_params = pika.ConnectionParameters(host=args.host)

  # Connect to the RabbitMQ server
  connection = pika.BlockingConnection(connection_params)

  # Create a channel
  channel = connection.channel()


  def consume(queue_name):
    """
    Consumes messages from the specified queue.

    Args:
        queue_name: The name of the queue to consume from.
    """
    # Declare the queue if it doesn't exist already
    channel.queue_declare(queue=queue_name)

    # Define a callback function for received messages
    channel.basic_consume(queue=queue_name, on_message_callback=on_message_received)

    # Start consuming messages (blocks until messages are received or connection is closed)
    channel.start_consuming()

  # Start consuming messages
  consume(args.queue_name)

# Close the connection (optional - will happen automatically when script exits)
# connection.close()