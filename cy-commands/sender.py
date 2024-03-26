import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())
import utils
import argparse



if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Send a message to a RabbitMQ queue.')
  parser.add_argument('queue_name', help='The name of the queue to send the message to.')
  parser.add_argument('message', help='The message content to send.')
  parser.add_argument('--host', help='host is optional default is localhost',default='localhost')
  args = parser.parse_args()

  # Send the message
  res = utils.send_message_and_wait(
    message = args.message,
    queue_name = args.queue_name,
    host = args.host

  )
  print(res)
