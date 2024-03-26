import argparse
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())
import utils
import argparse
import pika






if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Consume messages from a RabbitMQ queue.')
  parser.add_argument('queue_name', help='The name of the queue to consume from.')
  parser.add_argument('--host', help='The name of the queue to consume from.',default="localhost")
  args = parser.parse_args()

  # Define connection parameters (adjust if needed)
  connection_params = pika.ConnectionParameters(host=args.host)

  # Connect to the RabbitMQ server
  connection = pika.BlockingConnection(connection_params)

  # Create a channel
  channel = connection.channel()
  utils.create_listener(
    channel=channel,
    queue_name=args.queue_name,
    host = args.host
  )

