
import pika
import argparse

def send_message_to_queue(queue_name, message):
  """
  Sends a message to a specified queue on the RabbitMQ server at localhost.

  Args:
      queue_name: The name of the queue to send the message to.
      message: The message content to send as a string.
  """

  # Define connection parameters (adjust if needed)
  connection_params = pika.ConnectionParameters(host='localhost')

  try:
    # Connect to the RabbitMQ server
    connection = pika.BlockingConnection(connection_params)

    # Create a channel
    channel = connection.channel()

    # Publish the message to the queue
    channel.basic_publish(exchange='', routing_key=queue_name, body=message.encode())

    print(f" [x] Sent '{message}' to '{queue_name}'")

  except pika.exceptions.AMQPConnectionError as e:
    print(f"Error connecting to RabbitMQ: {e}")
  except Exception as e:  # Catch any other exceptions
    print(f"An error occurred: {e}")
  finally:
    # Close the connection (if established)
    if connection:
      connection.close()

if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Send a message to a RabbitMQ queue.')
  parser.add_argument('queue_name', help='The name of the queue to send the message to.')
  parser.add_argument('message', help='The message content to send.')
  args = parser.parse_args()

  # Send the message
  send_message_to_queue(args.queue_name, args.message)
